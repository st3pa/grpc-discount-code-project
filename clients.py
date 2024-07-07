import grpc
import argparse
import logging
from discount_proto import discount_pb2
from discount_proto import discount_pb2_grpc

class DiscountClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = discount_pb2_grpc.DiscountServiceStub(self.channel)

    def generate_codes(self, count, length):
        try:
            request = discount_pb2.GenerateRequest(count=count, length=length)
            response = self.stub.GenerateCodes(request)
            return response.result
        except grpc.RpcError as e:
            logging.error(f"RPC error: {e.code()}, {e.details()}")
            return False

    def use_code(self, code):
        try:
            request = discount_pb2.UseCodeRequest(code=code)
            response = self.stub.UseCode(request)
            return response.result == 1
        except grpc.RpcError as e:
            logging.error(f"RPC error: {e.code()}, {e.details()}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Discount Code Client')
    parser.add_argument('action', choices=['generate', 'use'], help='Action to perform')
    parser.add_argument('--count', type=int, default=10, help='Number of codes to generate')
    parser.add_argument('--length', type=int, choices=[7, 8], default=8, help='Length of the discount code')
    parser.add_argument('--code', type=str, help='Discount code to use')
    args = parser.parse_args()

    client = DiscountClient()

    if args.action == 'generate':
        result = client.generate_codes(args.count, args.length)
        if result:
            print(f"Successfully generated {args.count} codes of length {args.length}")
        else:
            print("Failed to generate codes")
    elif args.action == 'use':
        if not args.code:
            print("Please provide a code to use with --code")
            return
        result = client.use_code(args.code)
        if result:
            print(f"Successfully used code: {args.code}")
        else:
            print(f"Failed to use code or code already used: {args.code}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()