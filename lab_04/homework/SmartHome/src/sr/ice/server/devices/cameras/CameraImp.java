package sr.ice.server.devices.cameras;

import Smarthome.*;
import com.zeroc.Ice.Current;
import sr.ice.server.devices.DeviceImp;

public class CameraImp extends DeviceImp implements Camera {
    private String id;
    private Mode mode;
    private Location location;
    private int resolution;
    private double storageLevel;
    private final int MIN_RESOLUTION = 360;
    private final int MAX_RESOLUTION = 4320;

    public CameraImp(String id) {
        super(id);
        this.location = new Location(0, 0);
        this.resolution = 1080;
        this.storageLevel = 0.0;
    }

    public CameraImp(String id, Location location) {
        super(id);
        this.location = location;
        this.resolution = 1080;
        this.storageLevel = 0.0;
    }

    @Override
    public String getId(Current current) {
        return this.id;
    }

    @Override
    public void setMode(Mode mode, Current current) {
        System.out.println("Setting mode to " + mode + " for camera " + this.id);
        this.mode = mode;
    }

    @Override
    public Mode getMode(Current current) {
        return this.mode;
    }

    @Override
    public Location getLocation(Current current) throws DevicesIsInStandbyMode {
        if (this.mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }
        return this.location;
    }

    @Override
    public void setResolution(int resolution, Current current)
            throws DevicesIsInStandbyMode, InputResolutionOutOfRange, StorageFullError {
        if (this.mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        if (resolution < MIN_RESOLUTION || resolution > MAX_RESOLUTION) {
            throw new InputResolutionOutOfRange();
        }

        if (this.storageLevel > 95.0) {
            throw new StorageFullError();
        }

        System.out.println("Setting resolution to " + resolution + " for camera " + this.id);
        this.resolution = resolution;

        if (resolution > 1080) {
            this.storageLevel += 5.0;
            if (this.storageLevel > 100.0) {
                this.storageLevel = 100.0;
            }
        }
    }

    @Override
    public int getResolution(Current current) throws DevicesIsInStandbyMode {
        if (this.mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }
        return this.resolution;
    }

    @Override
    public double getStorageLevel(Current current) throws DevicesIsInStandbyMode {
        if (this.mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }
        return this.storageLevel;
    }
}
