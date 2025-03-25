import http.server
import socketserver
import os
import json
import cgi

PORT = 8000
FRONTEND_DIR = r"C:\Users\heman\OneDrive\Documents\Python projects\Mini project-5 sem\Jarvis\project trail 1\skinndisease\farmertrial1\frontend"
UPLOAD_DIR = os.path.join(FRONTEND_DIR, "uploads")
PRODUCTS_FILE = os.path.join(FRONTEND_DIR, "products.json")
ORDERS_FILE = os.path.join(FRONTEND_DIR, "orders.json")
FARMERS_FILE = os.path.join(FRONTEND_DIR, "farmers.json")

# Ensure directories and files exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
for file in [PRODUCTS_FILE, ORDERS_FILE, FARMERS_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f, indent=4)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == "/products":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with open(PRODUCTS_FILE, "r") as f:
                self.wfile.write(f.read().encode())
            return

        elif self.path.startswith("/uploads/"):
            file_path = os.path.join(FRONTEND_DIR, self.path.lstrip("/"))
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        self.directory = FRONTEND_DIR
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers.get("Content-Type", "")

        if self.path in ["/add_item", "/edit_item"]:
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})

            name = form.getvalue("name", "").strip()
            price = form.getvalue("price", "").strip()
            kg = form.getvalue("kg", "").strip()
            farmer = form.getvalue("farmer", "").strip()
            original_name = form.getvalue("originalName", "").strip()

            with open(PRODUCTS_FILE, "r+") as f:
                products = json.load(f)
                if self.path == "/edit_item":
                    products = [p for p in products if p["name"] != original_name]
                
                image_name = None
                if "image" in form and form["image"].filename:
                    image_field = form["image"]
                    image_name = os.path.basename(image_field.filename)
                    image_path = os.path.join(UPLOAD_DIR, image_name)  
                    with open(image_path, "wb") as f_img:
                        f_img.write(image_field.file.read())
                
                old_product = next((p for p in products if p["name"] == original_name), None)
                if not image_name and old_product:
                    image_name = old_product.get("image", "placeholder.png")

                products.append({"name": name, "price": price, "kg": kg, "farmer": farmer, "image": image_name or "placeholder.png"})
                f.seek(0)
                json.dump(products, f, indent=4)
                f.truncate()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Product saved successfully!"}).encode())

        elif self.path == "/delete_item":
            data = json.loads(self.rfile.read(content_length))
            name = data.get("name")
            with open(PRODUCTS_FILE, "r+") as f:
                products = [p for p in json.load(f) if p["name"] != name]
                f.seek(0)
                json.dump(products, f, indent=4)
                f.truncate()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Product deleted!"}).encode())

        elif self.path == "/submit_order":
            order_data = json.loads(self.rfile.read(content_length))
            with open(ORDERS_FILE, "r+") as f:
                orders = json.load(f)
                orders.append(order_data)
                f.seek(0)
                json.dump(orders, f, indent=4)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Order placed successfully!"}).encode())

        elif self.path == "/register_farmer":
            if "application/json" in content_type:
                data = json.loads(self.rfile.read(content_length))
                name, email, password = data.get("name", "").strip(), data.get("email", "").strip(), data.get("password", "").strip()
            else:
                form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                name, email, password = form.getvalue("name", "").strip(), form.getvalue("email", "").strip(), form.getvalue("password", "").strip()

            if not name or not email or not password:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "All fields are required"}).encode())
                return

            with open(FARMERS_FILE, "r+") as f:
                farmers = json.load(f)
                if any(farmer["email"] == email for farmer in farmers):
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Email already registered"}).encode())
                    return
                
                farmers.append({"name": name, "email": email, "password": password})
                f.seek(0)
                json.dump(farmers, f, indent=4)
                f.truncate()

            self.send_response(302)
            self.send_header("Location", "/farmer.html")
            self.end_headers()
            return

        else:
            self.send_response(404)
            self.end_headers()

os.chdir(FRONTEND_DIR)
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving on port {PORT}...")
    httpd.serve_forever()
