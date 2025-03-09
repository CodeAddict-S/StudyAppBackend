import os
import io
import zipfile
import qrcode
from PIL import Image, ImageDraw, ImageFont

base_dir = os.getcwd()


class Certificates:

    # Generate QR code
    @staticmethod
    def generate_qrcode(url, size=100):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white").convert("RGBA")
        datas = img.getdata()
        new_data = [
            (255, 255, 255, 0) if item[:3] == (255, 255, 255) else item
            for item in datas
        ]
        img.putdata(new_data)
        img = img.resize((size, size), Image.LANCZOS)
        return img

    @staticmethod
    def get_text_dimensions(text_string, font):
        _, descent = font.getmetrics()
        mask = font.getmask(text_string)
        bbox = mask.getbbox()
        if not bbox:
            return 0, 0  # Handle empty text
        text_width, text_height = bbox[2], bbox[3] + descent
        return text_width, text_height

    @staticmethod
    def generate_one_certificate(certificate):
        if not certificate.get("bg_image_path") or not certificate.get("name"):
            return None  # Skip if required data is missing

        try:
            img = Image.open(os.path.join(base_dir, certificate["bg_image_path"]))
        except FileNotFoundError:
            print(
                f"Warning: Background image {certificate['bg_image_path']} not found. Skipping..."
            )
            return None

        draw = ImageDraw.Draw(img)

        # Draw Texts
        for text in certificate.get("texts", []):
            if not all(k in text for k in ("content", "x", "y", "size")):
                continue

            font_path = os.path.join(
                base_dir, "static", "fonts", "Montserrat-Medium.ttf"
            )
            with open(font_path, "rb") as f:
                font_buffer = io.BytesIO(f.read())
                font_buffer.seek(0)
                font = ImageFont.truetype(font_buffer, size=text["size"])
                text_width, text_height = Certificates.get_text_dimensions(
                    text["content"], font
                )

                x, y = text["x"], text["y"] - (text_height // 5.5)
                draw.text(
                    xy=(x, y),
                    text=text["content"],
                    fill=(15, 15, 15),
                    font=font,
                    stroke_width=1.5,
                    stroke_fill=(15, 15, 15),
                )

        # Add QR Code (if present)
        if "qrcode" in certificate and "url" in certificate["qrcode"]:
            qr_data = certificate["qrcode"]
            qr_size = qr_data.get("size", 100)  # Default size if missing
            qrcode_img = Certificates.generate_qrcode(qr_data["url"], qr_size)

            qr_x, qr_y = qr_data.get("x", 0), qr_data.get("y", 0)
            img.paste(qrcode_img, (qr_x, qr_y), qrcode_img)

        # Save Image to Buffer
        buffer = io.BytesIO()
        img.convert("RGB").save(buffer, format="PNG")
        return {
            "name": certificate["name"],
            "content": buffer.getvalue(),
        }

    @staticmethod
    def generate_many_certificates(data: dict):
        if "certificates" not in data or not isinstance(data["certificates"], list):
            raise ValueError("Invalid data format: 'certificates' key must contain a list")

        images = []
        for certificate in data["certificates"]:
            image = Certificates.generate_one_certificate(certificate)
            if image:
                images.append(image)

        if not images:
            raise ValueError("No valid certificates were generated.")

        # Create an in-memory zip archive
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for image in images:
                zip_file.writestr(f"{image['name']}.png", image["content"])
        mem_zip.seek(0)
        return mem_zip.getvalue()
