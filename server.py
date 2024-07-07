import grpc
from concurrent import futures
import random
import string
import logging
import sqlite3
from typing import List
from discount_proto import discount_pb2
from discount_proto import discount_pb2_grpc


DEFAULT_COUNT = 1000
DEFAULT_LENGTH = 7

class DiscountCodeManager:
    def __init__(self, db_path: str = 'db-files/discounts.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS discount_codes
                (code TEXT PRIMARY KEY, used BOOLEAN NOT NULL DEFAULT 0)
            ''')

    def generate_code(self, length: int) -> str:
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not self._code_exists(code):
                self._save_code(code)
                return code

    def _code_exists(self, code: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM discount_codes WHERE code = ?", (code,))
            return cursor.fetchone() is not None

    def _save_code(self, code: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO discount_codes (code) VALUES (?)", (code,))

    def use_code(self, code: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE discount_codes SET used = 1 WHERE code = ? AND used = 0", (code,))
            return cursor.rowcount > 0

    def get_unused_codes(self) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code FROM discount_codes WHERE used = 0")
            return [row[0] for row in cursor.fetchall()]

class DiscountServicer(discount_pb2_grpc.DiscountServiceServicer):
    def __init__(self):
        self.code_manager = DiscountCodeManager()

    def GenerateCodes(self, request, context):
        if not 1 <= request.count <= 2000:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Count must be between 1 and 2000")
        if request.length not in (7, 8):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Length must be 7 or 8")

        try:
            for _ in range(request.count):
                self.code_manager.generate_code(request.length)
            return discount_pb2.GenerateResponse(result=True)
        except Exception as e:
            logging.error(f"Error generating codes: {e}")
            return discount_pb2.GenerateResponse(result=False)

    def UseCode(self, request, context):
        if len(request.code) not in (7, 8):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Code must be 7 or 8 characters long")

        result = self.code_manager.use_code(request.code)
        return discount_pb2.UseCodeResponse(result=1 if result else 0)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    discount_pb2_grpc.add_DiscountServiceServicer_to_server(DiscountServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()