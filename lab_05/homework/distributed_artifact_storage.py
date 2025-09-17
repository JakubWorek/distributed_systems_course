import ray
import time
import random
import math
import asyncio
import logging
import os
from typing import Dict, List, Optional, Tuple, Set, Any


# --- Configuration ---
NUM_DATANODES = int(os.environ.get("NUM_WORKERS", 3))
CHUNK_SIZE = 10
REPLICATION_FACTOR = 2
HEARTBEAT_INTERVAL = 5
CHECK_REPLICATION_INTERVAL = 10
REQUEST_TIMEOUT = 7.0

# --- Logging Setup ---
log_level_str = os.environ.get("LOGLEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logging.getLogger("ray").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- DataNode Actor ---
@ray.remote
class DataNode:
    """Actor representing a storage node."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._chunks: Dict[str, str] = {}
        self._alive = True
        self.logger = logging.getLogger(f"DataNode-{node_id[:8]}")
        self.logger.info(f"DataNode {self.node_id} started on Ray node {ray.get_runtime_context().get_node_id()}.")

    def _configure_logger(self):
        """Helper to configure logger once node_id is set."""
        if not hasattr(self, 'logger') or self.node_id == "pending":
            log_name = f"DataNode-{self.node_id[:8]}" if self.node_id != "pending" else "DataNode-PENDING"
            self.logger = logging.getLogger(log_name)
            if not self.logger.hasHandlers():
                pass
            self.logger.info(f"DataNode {self.node_id} started/configured on Ray node {ray.get_runtime_context().get_node_id()}.")

    def set_id(self, final_node_id: str) -> None:
        """Sets the final node ID after registration."""
        if self.node_id == "pending" or self.node_id != final_node_id:
            self.logger.info(f"Setting final node ID from '{self.node_id}' to '{final_node_id}'.")
            self.node_id = final_node_id
            self._configure_logger()
        else:
            self.logger.warning(f"Attempted to set node ID to '{final_node_id}', but it was already set.")

    def store_chunk(self, chunk_id: str, data: str) -> bool:
        if not self._alive:
            self.logger.warning(f"Received store request for {chunk_id} while failed.")
            return False
        self._chunks[chunk_id] = data
        return True

    def get_chunk(self, chunk_id: str) -> Optional[str]:
        if not self._alive:
            self.logger.warning(f"Received get request for {chunk_id} while failed.")
            return None
        return self._chunks.get(chunk_id)

    def delete_chunk(self, chunk_id: str) -> bool:
        if not self._alive:
            self.logger.warning(f"Received delete request for {chunk_id} while failed.")
            if chunk_id in self._chunks: del self._chunks[chunk_id]
            return True
        if chunk_id in self._chunks:
            del self._chunks[chunk_id]
            return True
        return False

    def get_stored_chunk_ids(self) -> List[str]:
        if not self._alive: return []
        return list(self._chunks.keys())

    def get_status(self) -> Dict[str, Any]:
        status = {
            "node_id": self.node_id,
            "ray_node_id": ray.get_runtime_context().get_node_id(),
            "state": "READY" if self._alive else "FAILED",
            "stored_chunks_count": len(self._chunks) if self._alive else 0,
            "stored_chunk_ids": list(self._chunks.keys()) if self._alive else []
        }
        return status

    def is_alive(self) -> bool:
        """Simple health check method."""
        return self._alive

    def simulate_failure(self):
        if self._alive:
            self.logger.warning(f"Simulating FAILURE.")
            self._alive = False

    def recover(self):
        if not self._alive:
            self.logger.warning(f"Simulating RECOVERY.")
            self._alive = True


# --- NameNode Actor ---
@ray.remote
class NameNode:
    """Actor managing the filesystem namespace and block locations."""
    def __init__(self, chunk_size: int, replication_factor: int):
        self.chunk_size = chunk_size
        self.replication_factor = replication_factor
        self.datanodes: Dict[str, ray.actor.ActorHandle] = {}
        self.live_datanodes: Set[str] = set()
        self.dead_datanodes: Set[str] = set()
        self.artifact_metadata: Dict[str, Dict[str, Any]] = {}
        self.chunk_locations: Dict[str, List[str]] = {}
        self._node_id_counter = 0
        self._background_tasks: List[asyncio.Task] = []
        self._stop_event = asyncio.Event()
        self.logger = logging.getLogger("NameNode")
        self.logger.info(f"NameNode started on Ray node {ray.get_runtime_context().get_node_id()}. ChunkSize={chunk_size}, ReplicationFactor={replication_factor}")
        self._start_background_tasks()

    def _start_background_tasks(self):
        self.logger.info("Starting background tasks (heartbeat, replication check)")
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._background_tasks.append(loop.create_task(self._heartbeat_loop()))
        self._background_tasks.append(loop.create_task(self._replication_check_loop()))

    async def stop_background_tasks(self):
        self.logger.info("Stopping background tasks...")
        self._stop_event.set()
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._background_tasks, return_exceptions=True),
                timeout=HEARTBEAT_INTERVAL + 2
            )
        except asyncio.TimeoutError:
            self.logger.warning("Timeout waiting for background tasks to stop.")
        except Exception as e:
            self.logger.error(f"Error during background task shutdown: {e}")
        self.logger.info("Background tasks stopped.")

    def _get_next_node_id(self) -> str:
        self._node_id_counter += 1
        return f"datanode-{self._node_id_counter}"

    def register_datanode(self, datanode_handle: ray.actor.ActorHandle) -> str:
        node_id = self._get_next_node_id()
        self.datanodes[node_id] = datanode_handle
        self.live_datanodes.add(node_id)
        self.logger.info(f"Registered DataNode {node_id}")
        return node_id
    
    async def ping(self) -> bool:
        """Simple method to check if the actor is alive and responsive."""
        return True

    def _get_live_node_handles(self) -> List[Tuple[str, ray.actor.ActorHandle]]:
        return [(nid, self.datanodes[nid]) for nid in self.live_datanodes if nid in self.datanodes]

    def _choose_datanodes(self, num_nodes: int, exclude_nodes: List[str] = []) -> List[Tuple[str, ray.actor.ActorHandle]]:
        live_nodes = self._get_live_node_handles()
        available_nodes = [(nid, h) for nid, h in live_nodes if nid not in exclude_nodes]

        required_nodes = min(num_nodes, len(available_nodes))

        if required_nodes <= 0:
            self.logger.warning(f"Not enough live datanodes ({len(available_nodes)}) to satisfy request for {num_nodes} (excluding {exclude_nodes})")
            return []

        return random.sample(available_nodes, required_nodes)

    async def upload_artifact(self, name: str, content: str) -> bool:
        if name in self.artifact_metadata:
            self.logger.error(f"Artifact '{name}' already exists. Use update_artifact.")
            return False

        current_live_nodes = len(self._get_live_node_handles())
        effective_replication = min(self.replication_factor, current_live_nodes)

        if effective_replication == 0:
            self.logger.error(f"No live datanodes available to store artifact '{name}'.")
            return False
        if effective_replication < self.replication_factor:
            self.logger.warning(f"Only {effective_replication} live datanodes available. Will store with reduced replication for artifact '{name}'.")

        self.logger.info(f"Uploading artifact '{name}' (size: {len(content)} bytes) with effective replication {effective_replication}")

        num_chunks = math.ceil(len(content) / self.chunk_size)
        chunks = {}
        chunk_ids = []
        for i in range(num_chunks):
            chunk_id = f"{name}_chunk_{i}"
            start = i * self.chunk_size
            end = start + self.chunk_size
            chunk_data = content[start:end]
            chunks[chunk_id] = chunk_data
            chunk_ids.append(chunk_id)

        pending_stores = {}
        all_chunk_tasks = []
        chunk_task_map = {}

        for chunk_id, chunk_data in chunks.items():
            chosen_nodes = self._choose_datanodes(effective_replication)
            if not chosen_nodes:
                self.logger.error(f"Failed to find ANY nodes for chunk {chunk_id} of artifact '{name}'. Aborting upload.")
                return False

            self.logger.debug(f"Storing chunk {chunk_id} on nodes: {[nid for nid, _ in chosen_nodes]}")
            chunk_task_map[chunk_id] = []
            for node_id, node_handle in chosen_nodes:
                future = node_handle.store_chunk.remote(chunk_id, chunk_data)
                all_chunk_tasks.append(future)
                chunk_task_map[chunk_id].append((future, node_id))

        new_chunk_locations = {}
        try:
            results_map = {}
            results = await asyncio.gather(*[asyncio.wait_for(f, timeout=REQUEST_TIMEOUT) for f in all_chunk_tasks], return_exceptions=True)
            for future, result in zip(all_chunk_tasks, results):
                results_map[future] = result

            all_successful = True
            for chunk_id, tasks in chunk_task_map.items():
                successful_nodes = []
                failed_nodes = []
                for future, node_id in tasks:
                    result = results_map[future]
                    if isinstance(result, Exception):
                        self.logger.warning(f"Error storing chunk {chunk_id} on node {node_id}: {result}")
                        failed_nodes.append(node_id)
                    elif result:
                        successful_nodes.append(node_id)
                    else:
                        self.logger.warning(f"Node {node_id} failed to store chunk {chunk_id} (returned False).")
                        failed_nodes.append(node_id)

                if not successful_nodes:
                    self.logger.error(f"Failed to store chunk {chunk_id} on ANY target node. Aborting upload.")
                    all_successful = False
                    break

                if len(successful_nodes) < len(tasks):
                    self.logger.warning(f"Chunk {chunk_id} stored on only {len(successful_nodes)}/{len(tasks)} attempted nodes.")

                new_chunk_locations[chunk_id] = successful_nodes

        except asyncio.TimeoutError:
            self.logger.error(f"Timeout waiting for chunk storage for artifact '{name}'. Aborting upload.")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during chunk storage gather for artifact '{name}': {e}. Aborting upload.")
            return False

        if not all_successful:
            self.logger.error(f"Upload failed for {name} due to storage errors. Rollback needed.")
            return False

        self.artifact_metadata[name] = {"chunk_ids": chunk_ids, "num_chunks": num_chunks}
        self.chunk_locations.update(new_chunk_locations)
        self.logger.info(f"Successfully uploaded artifact '{name}' ({num_chunks} chunks).")
        return True

    async def get_artifact(self, name: str) -> Optional[str]:
        self.logger.info(f"Getting artifact '{name}'")
        if name not in self.artifact_metadata:
            self.logger.error(f"Artifact '{name}' not found.")
            return None

        metadata = self.artifact_metadata[name]
        chunk_ids = metadata.get("chunk_ids", [])
        num_chunks = metadata.get("num_chunks", 0)

        if not chunk_ids or num_chunks == 0:
            self.logger.error(f"Artifact '{name}' has invalid metadata (no chunks).")
            return None

        reconstructed_chunks = {}
        chunk_fetch_info = {}
        fetch_tasks = []

        for i, chunk_id in enumerate(chunk_ids):
            if chunk_id not in self.chunk_locations:
                self.logger.error(f"Metadata inconsistency: Chunk {chunk_id} (index {i}) for artifact '{name}' not found in locations.")
                return None

            node_ids = self.chunk_locations[chunk_id]
            live_node_ids = [nid for nid in node_ids if nid in self.live_datanodes and nid in self.datanodes]

            if not live_node_ids:
                self.logger.error(f"Chunk {chunk_id} (index {i}) for artifact '{name}' has no LIVE replicas. Locations: {node_ids}, LiveSet: {self.live_datanodes}. Cannot reconstruct.")
                return None

            node_id_to_try = random.choice(live_node_ids)
            node_handle = self.datanodes[node_id_to_try]
            self.logger.debug(f"Scheduling fetch for chunk {chunk_id} (index {i}) from node {node_id_to_try}")
            obj_ref = node_handle.get_chunk.remote(chunk_id)
            fetch_tasks.append(obj_ref)
            chunk_fetch_info[chunk_id] = {
                "index": i,
                "chosen_node": node_id_to_try,
                "all_live_nodes": live_node_ids,
                "obj_ref": obj_ref,
                "data": None
            }

        try:
            results = ray.get(fetch_tasks, timeout=REQUEST_TIMEOUT * len(fetch_tasks))
            results_map = {ref: res for ref, res in zip(fetch_tasks, results)}

            missing_chunks = False
            for chunk_id, info in chunk_fetch_info.items():
                obj_ref = info["obj_ref"]
                result = results_map.get(obj_ref)
                node_id_tried = info["chosen_node"]

                if result is None:
                    self.logger.warning(f"Node {node_id_tried} returned None for chunk {chunk_id} (chunk missing on node?).")                    
                    self.logger.error(f"Chunk {chunk_id} fetch returned None. Retry logic not implemented. Cannot reconstruct.")
                    missing_chunks = True
                    break
                else:
                    chunk_data = result
                    self.logger.debug(f"Successfully got chunk {chunk_id} from node {node_id_tried}")
                    reconstructed_chunks[info["index"]] = chunk_data

            if missing_chunks:
                return None

        except ray.exceptions.RayError as e:
            self.logger.error(f"Error during ray.get for chunk fetches for artifact '{name}': {e}. Handling potential node failure.")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error/timeout during chunk fetch for artifact '{name}': {e}. Cannot reconstruct.")
            return None


        if len(reconstructed_chunks) != num_chunks:
            self.logger.error(f"Retrieved {len(reconstructed_chunks)} chunks, but expected {num_chunks} for artifact '{name}'. Failed reconstruction.")
            return None

        content_parts = [reconstructed_chunks[i] for i in range(num_chunks)]
        full_content = "".join(content_parts)

        self.logger.info(f"Successfully retrieved artifact '{name}'.")
        return full_content
    
    async def update_artifact(self, name: str, new_content: str) -> bool:
        self.logger.info(f"Updating artifact '{name}'")
        if name not in self.artifact_metadata:
            self.logger.error(f"Artifact '{name}' not found for update.")
            return False

        self.logger.info(f"Deleting old version of '{name}' before update.")
        deleted = await self.delete_artifact(name, is_update=True)
        if not deleted:
            pass

        self.logger.info(f"Uploading new version of '{name}'.")
        uploaded = await self.upload_artifact(name, new_content)
        if not uploaded:
            self.logger.error(f"Failed to upload new version of artifact '{name}' during update.")
            return False

        self.logger.info(f"Successfully updated artifact '{name}'.")
        return True

    async def delete_artifact(self, name: str, is_update: bool = False) -> bool:
        if not is_update:
            self.logger.info(f"Deleting artifact '{name}'")

        metadata = self.artifact_metadata.pop(name, None)
        if metadata is None:
            if not is_update:
                self.logger.error(f"Artifact '{name}' not found for deletion.")
            return False if not is_update else True

        chunk_ids_to_delete = metadata.get("chunk_ids", [])
        if not chunk_ids_to_delete:
            self.logger.warning(f"No chunk IDs found in metadata for artifact '{name}' during deletion.")
            return True

        self.logger.debug(f"Deleting chunks for artifact '{name}': {chunk_ids_to_delete}")

        delete_tasks_obj_refs = []
        chunk_node_map = {}

        for chunk_id in list(chunk_ids_to_delete):
            node_ids = self.chunk_locations.pop(chunk_id, None)
            if node_ids:
                chunk_node_map[chunk_id] = []
                for node_id in node_ids:
                    if node_id in self.datanodes:
                        node_handle = self.datanodes[node_id]
                        obj_ref = node_handle.delete_chunk.remote(chunk_id)
                        delete_tasks_obj_refs.append(obj_ref)
                        chunk_node_map[chunk_id].append(node_id)
                    else:
                        self.logger.warning(f"Node {node_id} handle not found during delete of {chunk_id}.")


        if delete_tasks_obj_refs:
            self.logger.debug(f"Waiting for {len(delete_tasks_obj_refs)} chunk delete calls...")
            try:
                ray.get(delete_tasks_obj_refs, timeout=REQUEST_TIMEOUT * 2)
                self.logger.debug(f"Delete calls for artifact '{name}' likely completed.")
            except ray.exceptions.RayError as e:
                self.logger.warning(f"Error during ray.get for chunk deletion for artifact '{name}': {e}. Proceeding.")
            except Exception as e:
                self.logger.warning(f"Unexpected error/timeout during chunk deletion for artifact '{name}': {e}. Proceeding.")

        if not is_update:
            self.logger.info(f"Successfully deleted artifact '{name}'.")
        return True

    async def list_status(self) -> Dict[str, Any]:
        self.logger.info("Gathering cluster status...")
        datanode_statuses = {}
        status_tasks = []
        node_ids_for_tasks = []

        all_registered_node_ids = list(self.datanodes.keys())

        for node_id in all_registered_node_ids:
            node_handle = self.datanodes[node_id]
            status_tasks.append(node_handle.get_status.remote())
            node_ids_for_tasks.append(node_id)

        current_live_set = self.live_datanodes.copy()
        current_dead_set = self.dead_datanodes.copy()

        if status_tasks:
            try:
                results = await asyncio.gather(
                    *[asyncio.wait_for(f, timeout=REQUEST_TIMEOUT) for f in status_tasks],
                    return_exceptions=True
                )
                for i, result in enumerate(results):
                    node_id = node_ids_for_tasks[i]
                    if isinstance(result, Exception):
                        self.logger.warning(f"Failed to get status from node {node_id}: {result}. Marking as FAILED.")
                        datanode_statuses[node_id] = {"node_id": node_id, "state": "FAILED (unresponsive)", "error": str(result)}
                        if node_id in current_live_set:
                            await self._handle_node_failure(node_id)
                    else:
                        datanode_statuses[node_id] = result
                        node_reported_state = result.get("state")
                        if node_reported_state == "READY" and node_id in current_dead_set:
                            self.logger.info(f"Node {node_id} responded READY, marking as LIVE.")
                            self.dead_datanodes.discard(node_id)
                            self.live_datanodes.add(node_id)
                        elif node_reported_state == "FAILED" and node_id in current_live_set:
                            self.logger.warning(f"Node {node_id} reported FAILED state, marking as DEAD.")
                            await self._handle_node_failure(node_id)
                        elif node_reported_state == "READY" and node_id not in current_live_set:
                            self.logger.info(f"Node {node_id} responded READY and was not in live set. Adding.")
                            self.live_datanodes.add(node_id)
                            self.dead_datanodes.discard(node_id)

            except asyncio.TimeoutError:
                self.logger.error(f"Timeout gathering datanode statuses.")
            except Exception as e:
                self.logger.error(f"Error gathering datanode statuses: {e}")

        status = {
            "name_node_summary": {
                "ray_node_id": ray.get_runtime_context().get_node_id(),
                "total_registered_nodes": len(self.datanodes),
                "live_nodes": len(self.live_datanodes),
                "dead_nodes": len(self.dead_datanodes),
                "total_artifacts": len(self.artifact_metadata),
                "total_chunks_tracked": len(self.chunk_locations),
                "replication_factor": self.replication_factor,
                "chunk_size": self.chunk_size,
            },
            "artifact_details": self.artifact_metadata,
            "chunk_locations": self.chunk_locations,
            "datanode_status": dict(sorted(datanode_statuses.items())),
            "live_node_ids": sorted(list(self.live_datanodes)),
            "dead_node_ids": sorted(list(self.dead_datanodes))
        }
        return status

    async def _handle_node_failure(self, node_id: str):
        if node_id in self.live_datanodes:
            self.logger.warning(f"Node {node_id} failure detected. Marking as dead.")
            self.live_datanodes.discard(node_id)
            self.dead_datanodes.add(node_id)
        elif node_id not in self.datanodes:
            self.logger.error(f"Attempted to handle failure for unknown or already removed node {node_id}")

    async def _heartbeat_loop(self):
        self.logger.info("Heartbeat loop started.")
        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=HEARTBEAT_INTERVAL)
                break
            except asyncio.TimeoutError:
                pass

            if self._stop_event.is_set(): break

            nodes_to_check = list(self.live_datanodes)
            if not nodes_to_check: continue

            self.logger.debug(f"Sending heartbeats to {len(nodes_to_check)} live nodes...")
            futures = []
            node_ids_for_futures = []
            for node_id in nodes_to_check:
                if node_id in self.datanodes:
                    futures.append(self.datanodes[node_id].is_alive.remote())
                    node_ids_for_futures.append(node_id)
                else:
                    self.logger.warning(f"Heartbeat: Node {node_id} in live set but not in datanodes dict. Removing.")
                    self.live_datanodes.discard(node_id)

            if not futures: continue

            try:
                results = await asyncio.gather(
                     *[asyncio.wait_for(f, timeout=REQUEST_TIMEOUT) for f in futures],
                    return_exceptions=True
                )
                for i, result in enumerate(results):
                    node_id = node_ids_for_futures[i]
                    if node_id not in self.live_datanodes: continue
                    if isinstance(result, (ray.exceptions.RayActorError, asyncio.TimeoutError, Exception)):
                        self.logger.warning(f"Heartbeat failed for node {node_id}: {type(result).__name__}. Marking as dead.")
                        await self._handle_node_failure(node_id)
                    elif result is False:
                        self.logger.warning(f"Node {node_id} reported not alive via heartbeat. Marking as dead.")
                        await self._handle_node_failure(node_id)

            except asyncio.TimeoutError:
                self.logger.error(f"Timeout during heartbeat gather.")
            except Exception as e:
                self.logger.error(f"Error during heartbeat check gather: {e}")

        self.logger.info("Heartbeat loop stopped.")

    async def _replication_check_loop(self):
        self.logger.info("Replication check loop started.")
        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=CHECK_REPLICATION_INTERVAL)
                break
            except asyncio.TimeoutError:
                pass

            if self._stop_event.is_set(): break

            self.logger.info("Running replication check...")
            under_replicated_chunks = []
            all_chunk_ids = list(self.chunk_locations.keys())

            for chunk_id in all_chunk_ids:
                if chunk_id not in self.chunk_locations: continue
                locations = self.chunk_locations[chunk_id]
                live_replicas = [nid for nid in locations if nid in self.live_datanodes and nid in self.datanodes]
                current_replication = len(live_replicas)

                if current_replication < self.replication_factor:
                    self.logger.warning(f"Chunk {chunk_id} is under-replicated (found {current_replication}/{self.replication_factor} live replicas).")
                    if current_replication == 0:
                        self.logger.error(f"CRITICAL: Chunk {chunk_id} has NO live replicas!")
                        continue
                    under_replicated_chunks.append((chunk_id, live_replicas, locations))

            if not under_replicated_chunks:
                self.logger.info("Replication check complete.")
                continue

            replication_tasks = [
                self._replicate_chunk(chunk_id, live_replicas, all_locations)
                for chunk_id, live_replicas, all_locations in under_replicated_chunks
            ]
            if replication_tasks:
                self.logger.info(f"Executing {len(replication_tasks)} re-replication tasks concurrently...")
                await asyncio.gather(*replication_tasks, return_exceptions=True)
                self.logger.info("Re-replication task batch finished.")

        self.logger.info("Replication check loop stopped.")

    async def _replicate_chunk(self, chunk_id: str, live_replicas: List[str], all_locations: List[str]):
        if chunk_id not in self.chunk_locations: return
        current_live_replicas = [nid for nid in self.chunk_locations[chunk_id] if nid in self.live_datanodes and nid in self.datanodes]
        if len(current_live_replicas) >= self.replication_factor: return
        if not current_live_replicas:
            self.logger.error(f"Replication failed for {chunk_id}: No live source replica found.")
            return

        needed_replicas = self.replication_factor - len(current_live_replicas)
        source_node_id = random.choice(current_live_replicas)

        if source_node_id not in self.datanodes:
            self.logger.error(f"Source node {source_node_id} handle not found for chunk {chunk_id}. Skipping replication.")
            return
        source_handle = self.datanodes[source_node_id]

        target_nodes = self._choose_datanodes(needed_replicas, exclude_nodes=all_locations)
        if not target_nodes:
            self.logger.warning(f"Could not find {needed_replicas} new nodes to replicate chunk {chunk_id}.")
            return

        chunk_data = None
        try:
            chunk_data = await asyncio.wait_for(source_handle.get_chunk.remote(chunk_id), timeout=REQUEST_TIMEOUT)
            if chunk_data is None:
                self.logger.error(f"Source node {source_node_id} returned None for chunk {chunk_id}. Cannot re-replicate.")
                return
        except (asyncio.TimeoutError, ray.exceptions.RayActorError) as e:
            self.logger.error(f"Failed to get chunk {chunk_id} from source node {source_node_id}: {e}. Marking source dead.")
            await self._handle_node_failure(source_node_id)
            return
        except Exception as e:
            self.logger.error(f"Unexpected error getting chunk {chunk_id} from source {source_node_id}: {e}")
            return

        store_futures = []
        target_node_ids = [nid for nid, _ in target_nodes]
        self.logger.info(f"Re-replicating chunk {chunk_id} from {source_node_id} to nodes: {target_node_ids}")
        for node_id, node_handle in target_nodes:
            store_futures.append(node_handle.store_chunk.remote(chunk_id, chunk_data))

        try:
            results = await asyncio.gather(*[asyncio.wait_for(f, timeout=REQUEST_TIMEOUT) for f in store_futures], return_exceptions=True)
            successful_stores = []
            for i, result in enumerate(results):
                target_node_id = target_node_ids[i]
                if isinstance(result, Exception) or not result:
                    self.logger.warning(f"Failed or error storing re-replicated chunk {chunk_id} on target {target_node_id}: {result}")
                else:
                    successful_stores.append(target_node_id)

            if successful_stores:
                current_locations = self.chunk_locations.get(chunk_id, [])
                new_location_set = set(current_locations) | set(successful_stores)
                self.chunk_locations[chunk_id] = list(new_location_set)
                self.logger.info(f"Successfully re-replicated chunk {chunk_id} to {len(successful_stores)} new nodes.")

        except asyncio.TimeoutError:
            self.logger.error(f"Timeout storing re-replicated chunk {chunk_id}.")
        except Exception as e:
            self.logger.error(f"Unexpected error storing re-replicated chunk {chunk_id}: {e}")



# --- Client Functions ---
async def client_upload(nn_handle, name, content):
    logger.info(f"Client: Uploading artifact: {name}")
    success = await nn_handle.upload_artifact.remote(name, content)
    logger.info(f"Client: Upload successful: {success}")
    return success

async def client_update(nn_handle, name, content):
    logger.info(f"Client: Updating artifact: {name}")
    success = await nn_handle.update_artifact.remote(name, content)
    logger.info(f"Client: Update successful: {success}")
    return success

async def client_get(nn_handle, name):
    logger.info(f"Client: Getting artifact: {name}")
    content = await nn_handle.get_artifact.remote(name)
    if content is not None:
        logger.info(f"Client: Retrieved content ({len(content)} bytes): '{content[:50]}{'...' if len(content)>50 else ''}'")
    else:
        logger.warning(f"Client: Failed to retrieve artifact '{name}'.")
    return content

async def client_delete(nn_handle, name):
    logger.info(f"Client: Deleting artifact: {name}")
    success = await nn_handle.delete_artifact.remote(name)
    logger.info(f"Client: Delete successful: {success}")
    return success

async def client_list_status(nn_handle):
    logger.info("Client: Listing Cluster Status...")
    try:
        status = await asyncio.wait_for(nn_handle.list_status.remote(), timeout=REQUEST_TIMEOUT * 1.5)
        print("\n--- Cluster Status ---")
        print("NameNode Summary:")
        if status.get("name_node_summary"):
            for key, value in status["name_node_summary"].items():
                print(f"  {key}: {value}")
        else: print("  Unavailable")
        print("\nArtifact Details:")
        if status.get("artifact_details"):
            for name, meta in status["artifact_details"].items():
                print(f"  Artifact '{name}': {meta.get('num_chunks','N/A')} chunks ({meta.get('chunk_ids',[])})")
        else: print("  No artifacts found.")
        print("\nChunk Locations:")
        if status.get("chunk_locations"):
            live_node_ids = status.get("live_node_ids",[])
            dead_node_ids = status.get("dead_node_ids",[])
            for chunk_id, nodes in status["chunk_locations"].items():
                live_nodes = [n for n in nodes if n in live_node_ids]
                dead_nodes = [n for n in nodes if n in dead_node_ids]
                unknown_nodes = [n for n in nodes if n not in live_node_ids and n not in dead_node_ids]
                print(f"  Chunk '{chunk_id}': Live={live_nodes}, Dead={dead_nodes}, Unknown={unknown_nodes} (Total Tracked: {len(nodes)})")
        else: print("  No chunk locations tracked.")
        print("\nDataNode Status:")
        if status.get("datanode_status"):
            for node_id, dn_status in status["datanode_status"].items():
                state = dn_status.get('state', 'UNKNOWN')
                count = dn_status.get('stored_chunks_count', 'N/A')
                ray_node = dn_status.get('ray_node_id', 'N/A')[:8]
                print(f"  Node '{node_id}': State={state}, Chunks={count}, RayNode={ray_node}...")
        else: print("  No datanode status available.")
        print("-" * 30)
    except asyncio.TimeoutError:
        logger.error("Client: Timeout listing cluster status.")
    except Exception as e:
        logger.error(f"Client: Error listing cluster status: {e}")

# --- Simulate Failure ---
async def simulate_random_failure(datanodes: Dict[str, ray.actor.ActorHandle]):
    logger.info("Client: Simulating Random DataNode Failure")

    live_node_ids = []
    check_tasks = []
    nodes_to_check = list(datanodes.keys())

    async def check_node_alive(node_id, handle):
        try:
            if await asyncio.wait_for(handle.is_alive.remote(), timeout=1.0):
                return node_id
        except:
            pass
        return None

    async def get_live_ids():
        tasks = [check_node_alive(nid, h) for nid, h in datanodes.items()]
        results = await asyncio.gather(*tasks)
        return [nid for nid in results if nid]

    live_node_ids = await get_live_ids()

    if not live_node_ids:
        logger.warning("Client: No live nodes found to simulate failure.")
        return None

    node_id_to_fail = random.choice(live_node_ids)
    handle_to_fail = datanodes[node_id_to_fail]

    logger.warning(f"Client: Simulating failure on node: {node_id_to_fail}")
    try:
        ray.kill(handle_to_fail, no_restart=True)
        logger.info(f"Client: Failure simulation signal sent to {node_id_to_fail}. NameNode will detect via heartbeat or next interaction.")
        return node_id_to_fail
    except Exception as e:
        logger.error(f"Client: Error sending failure signal to {node_id_to_fail}: {e}")
        return None


# --- Main Execution Logic ---
async def main():
    ray_address = os.environ.get("RAY_ADDRESS")
    ray_password = os.environ.get("RAY_PASSWORD")

    if not ray_address:
        logger.error("RAY_ADDRESS environment variable not set. Cannot connect.")
        return

    logger.info(f"Attempting to connect Ray Client to: {ray_address}")
    try:
        ray.init(
            address=ray_address,
            namespace="artifact_storage",
            logging_level=logging.WARNING,
            _redis_password=ray_password if ray_password else None
        )
        logger.info("Ray Client Connected.")
        logger.info(f"Ray Cluster Resources: {ray.cluster_resources()}")

    except ConnectionError as e:
        logger.exception(f"!!!!!!!! FAILED Ray Init !!!!!!!! Connection Error: {e}")
        return
    except Exception as e:
        logger.exception(f"!!!!!!!! FAILED Ray Init !!!!!!!! General Error: {e}")
        return


    name_node = None
    data_nodes = {}
    try:
        nn_actor_name = "NameNodeActor"
        logger.info(f"Getting or creating NameNode actor '{nn_actor_name}'...")
        name_node = NameNode.options(
            name=nn_actor_name,
            get_if_exists=True,
        ).remote(
            chunk_size=CHUNK_SIZE,
            replication_factor=REPLICATION_FACTOR
        )
        logger.info(f"NameNode Actor handle obtained/created: {name_node}")
        try:
            await name_node.ping.remote()
            logger.info("NameNode actor is responsive.")
        except Exception as e:
            logger.error(f"Failed to ping NameNode actor after getting handle: {e}")
            return

        logger.info(f"Creating {NUM_DATANODES} DataNode Actors...")
        data_node_handles = [DataNode.remote("pending") for _ in range(NUM_DATANODES)]

        register_tasks = [name_node.register_datanode.remote(h) for h in data_node_handles]
        registered_ids = await asyncio.gather(*register_tasks)

        set_id_obj_refs = []
        data_nodes = {}
        for handle, node_id in zip(data_node_handles, registered_ids):
            if node_id:
                data_nodes[node_id] = handle
                obj_ref = handle.set_id.remote(node_id)
                set_id_obj_refs.append(obj_ref)
            else:
                logger.error(f"Failed to register a DataNode handle.")

        if set_id_obj_refs:
            logger.info(f"Sending final IDs to {len(set_id_obj_refs)} registered DataNodes...")
            try:
                ray.get(set_id_obj_refs, timeout=REQUEST_TIMEOUT * 2)
                logger.info(f"Final IDs assigned to DataNodes.")
            except ray.exceptions.RayError as e:
                logger.error(f"Error assigning final IDs to DataNodes: {e}")
            except Exception as e:
                logger.error(f"Unexpected error waiting for set_id calls: {e}")

        else:
            logger.warning("No DataNodes were successfully registered or assigned IDs.")


        logger.info(f"Successfully configured {len(data_nodes)} DataNodes: {list(data_nodes.keys())}")



        # --- Verification Tests ---
        logger.info("Starting verification tests...")
        await client_list_status(name_node)
        await asyncio.sleep(1)

        artifact1_content = "Distributed artifact content, first version. " * 5
        await client_upload(name_node, "dist-artifact-1", artifact1_content)
        await client_list_status(name_node)
        await asyncio.sleep(1)

        artifact2_content = "Second artifact, shorter."
        await client_upload(name_node, "dist-artifact-2", artifact2_content)
        await client_list_status(name_node)
        await asyncio.sleep(1)

        retrieved_content = await client_get(name_node, "dist-artifact-1")
        assert retrieved_content == artifact1_content, "Content verification FAILED for dist-artifact-1!"
        logger.info("Content verification PASSED for dist-artifact-1.")
        await asyncio.sleep(1)

        updated_content = "Distributed artifact content, UPDATED version. " * 4
        await client_update(name_node, "dist-artifact-1", updated_content)
        await client_list_status(name_node)
        await asyncio.sleep(1)

        retrieved_updated_content = await client_get(name_node, "dist-artifact-1")
        assert retrieved_updated_content == updated_content, "Content verification FAILED for updated dist-artifact-1!"
        logger.info("Content verification PASSED for updated dist-artifact-1.")
        await asyncio.sleep(1)

        if data_nodes:
            failed_node_id = await simulate_random_failure(data_nodes)
            if failed_node_id:
                wait_time = HEARTBEAT_INTERVAL + CHECK_REPLICATION_INTERVAL + 3
                logger.info(f"Waiting {wait_time}s for failure detection/replication...")
                await asyncio.sleep(wait_time)
                await client_list_status(name_node)

                logger.info(f"Attempting get after node {failed_node_id} failure simulation...")
                retrieved_after_fail = await client_get(name_node, "dist-artifact-1")
                assert retrieved_after_fail == updated_content, f"Content verification FAILED after failure ({failed_node_id})!"
                logger.info(f"Content verification PASSED after failure ({failed_node_id}).")
                await asyncio.sleep(1)
            else:
                logger.warning("Failure simulation did not select a node to fail.")
        else:
            logger.warning("Skipping failure simulation as no DataNodes were registered.")

        await client_delete(name_node, "dist-artifact-2")
        await client_list_status(name_node)
        await asyncio.sleep(1)

        logger.info("Attempting to get deleted artifact dist-artifact-2...")
        deleted_content = await client_get(name_node, "dist-artifact-2")
        assert deleted_content is None, "Verification FAILED: Deleted artifact was retrieved!"
        logger.info("Verification PASSED: Deleted artifact is not retrievable.")

        await client_list_status(name_node)
        logger.info("Verification tests complete. All checks passed.")
        logger.info("All verification tests completed successfully.")


    except Exception as e:
        logger.exception(f"An error occurred in the main client execution: {e}")
    finally:
        if name_node:
            try:
                logger.info("Requesting NameNode to stop background tasks...")
                await name_node.stop_background_tasks.remote()
            except Exception as e:
                logger.error(f"Error stopping NameNode background tasks: {e}")

        logger.info("Disconnecting Ray client...")
        ray.shutdown()
        logger.info("Ray client disconnected.")


if __name__ == "__main__":
    asyncio.run(main())