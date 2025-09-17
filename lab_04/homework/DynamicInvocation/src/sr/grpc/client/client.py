import os
import grpc
import subprocess
import json
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import ProtoReflectionDescriptorDatabase
from google.protobuf.descriptor_pool import DescriptorPool

HOST='localhost'
PORT=50051

def get_service(desc_pool):
    service_desc = None
    service_name = None

    while service_desc is None:
        try:
            service_name = input("Wpisz nazwe serwisu: ")
            service_desc = desc_pool.FindServiceByName(service_name)
            if service_desc is None:
                print("Serwis nie znaleziony. Spróbuj ponownie.")
        except KeyError:
            print("Serwis nie znaleziony. Spróbuj ponownie.")
        except Exception as e:
            print(f"Błąd: {e}")
            exit(1)
    return service_desc, service_name


def print_serive_methods(service_desc):
    print(f"Metody dostępne w serwisie {service_desc.full_name}:")
    for method_name, method_desc in service_desc.methods_by_name.items():
        print(f"- {method_name}")
        
        stream_type = get_streaming_type(method_desc)
        print(f"  Typ strumieniowania: {stream_type}")

        input_type = method_desc.input_type
        print(f"  Typ wejścia: {input_type.full_name}")
        for field in input_type.fields:
            print(f"    Nazwa pola: {field.name}, typ: {get_field_type(field.type)}, etykieta: {get_field_label(field.label)}")


def get_streaming_type(method_desc):
    if method_desc.client_streaming:
        return "CLIENT_STREAMING"
    elif method_desc.server_streaming:
        return "SERVER_STREAMING"
    else:
        return "UNARY"

def get_field_type(field_type):
    if field_type == 1:
        return "double"
    elif field_type == 2:
        return "float"
    elif field_type == 3:
        return "int64"
    elif field_type == 4:
        return "uint64"
    elif field_type == 5:
        return "int32"
    return "unknown"

def get_field_label(field_label):
    if field_label == 1:
        return "OPTIONAL"
    elif field_label == 2:
        return "REQUIRED"
    elif field_label == 3:
        return "REPEATED"
    return "unknown"


def main():
    channel = grpc.insecure_channel('localhost:50051')
    reflection_db = ProtoReflectionDescriptorDatabase(channel)
    desc_pool = DescriptorPool(reflection_db)

    print("Dostępne serwisy:")
    services = reflection_db.get_services()
    print(services)

    service_desc, service_name = get_service(desc_pool)
    print_serive_methods(service_desc)

    while True:
        request = input(">>> ")

        if request == 'exit':
            break

        if request == 'list':
            print_serive_methods(service_desc)
            continue

        if request == 'help':
            print('Przykłady użycia:')
            print('Method {"param1":value1,"param2":value2} - wywołanie zwykłej metody')
            print('Method {"param1":value1,"param2":value2} --stream - wywołanie metody jako strumieniowej')
            print('Method --stream - rozpoczęcie strumieniowania do serwera (dla client streaming)')
            print('exit - zakończenie')
            print('list - wyświetlenie dostępnych metod')
            continue

        try:
            stream_flag = '--stream'
            is_streaming_requested = stream_flag in request
            
            if is_streaming_requested:
                request = request.replace(stream_flag, '').strip()
            
            parts = request.split(' ', 1)
            method_name = parts[0]

            try:
                method_desc = service_desc.methods_by_name[method_name]
            except KeyError:
                print(f"Metoda {method_name} nie istnieje. Użyj 'list' aby zobaczyć dostępne metody.")
                continue
            
            stream_type = get_streaming_type(method_desc)
            
            args_dict = {}
            if len(parts) > 1:
                try:
                    args_dict = json.loads(parts[1])
                except json.JSONDecodeError:
                    print("Nieprawidłowy format JSON dla argumentów. Użyj {'param1': value1, 'param2': value2}")
                    continue
            
            if stream_type == "UNARY":
                if len(parts) <= 1:
                    print("Brakujące argumenty dla metody")
                    continue
                
                if is_streaming_requested:
                    handle_server_streaming(service_name, method_name, args_dict)
                else:
                    handle_unary_call(service_name, method_name, args_dict)
                    
            elif stream_type == "SERVER_STREAMING":
                if len(parts) <= 1:
                    print("Brakujące argumenty dla metody strumieniowej")
                    continue
                handle_server_streaming(service_name, method_name, args_dict)
                
            elif stream_type == "CLIENT_STREAMING":
                handle_client_streaming(service_name, method_name)

            
        except IndexError:
            print("Nieprawidłowe zapytanie. Użyj 'help' aby zobaczyć przykłady.")
            continue
        except Exception as e:
            print(f"Nieoczekiwany błąd: {e}")
            continue


def handle_unary_call(service_name, method_name, args_dict):
    print(f"Wywołanie metody: {method_name}")
    print(f"Argumenty: {args_dict}")

    grpcurl_command = [
        '.\grpcurl',
        '-plaintext',
        '-d', json.dumps(args_dict),
        f'{HOST}:{PORT}',
        f'{service_name}/{method_name}'
    ]

    print(f"Wykonuję polecenie: {' '.join(grpcurl_command)}")
    result = subprocess.run(grpcurl_command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Błąd: {result.stderr}")


def handle_server_streaming(service_name, method_name, args_dict):
    print(f"Strumieniowanie z serwera dla metody: {method_name}")
    print(f"Argumenty: {args_dict}")
    
    grpcurl_command = [
        '.\grpcurl',
        '-plaintext',
        '-d', json.dumps(args_dict),
        f'{HOST}:{PORT}',
        f'{service_name}/{method_name}'
    ]

    print(f"Wykonuję polecenie: {' '.join(grpcurl_command)}")
    process = subprocess.Popen(grpcurl_command, stdout=subprocess.PIPE, text=True)

    for line in process.stdout:
        line = line.strip()
        if line:
            try:
                response_json = json.loads(line)
                print(f"Otrzymano: {response_json}")
            except json.JSONDecodeError:
                print(f"Otrzymano: {line}")
    
    process.wait()
    print("Strumieniowanie zakończone")


def handle_client_streaming(service_name, method_name):
    print(f"Strumieniowanie do serwera dla metody: {method_name}")
    print("Wprowadź dane w formacie JSON, po jednym na linię. Wprowadź 'end' aby zakończyć.")
    
    temp_input_file = "client_stream_input.json"
    
    with open(temp_input_file, 'w') as f:
        while True:
            line = input("Data> ")
            if line.lower() == 'end':
                break
            
            try:
                json_data = json.loads(line)
                f.write(line + "\n")
                print(f"Dodano: {json_data}")
            except json.JSONDecodeError:
                print("Nieprawidłowy format JSON. Spróbuj ponownie.")
    
    grpcurl_command = [
        '.\grpcurl',
        '-plaintext',
        '-d', '@',
        f'{HOST}:{PORT}',
        f'{service_name}/{method_name}'
    ]
    
    with open(temp_input_file, 'r') as f:
        print(f"Wykonuję polecenie: {' '.join(grpcurl_command)}")
        result = subprocess.run(grpcurl_command, 
                              input=f.read(), 
                              capture_output=True, 
                              text=True)

    if result.stdout:
        try:
            response_json = json.loads(result.stdout)
            print(f"Odpowiedź: {response_json}")
        except json.JSONDecodeError:
            print(f"Odpowiedź: {result.stdout}")
    
    if result.stderr:
        print(f"Błąd: {result.stderr}")

    try:
        os.remove(temp_input_file)
    except:
        pass


if __name__ == '__main__':
    main()