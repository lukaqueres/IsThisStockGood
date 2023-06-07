"""
Create preview images by tickers with PIL(low) library
"""
import io
from PIL import Image, ImageFont, ImageDraw


def _values(node, kv):
	if isinstance(node, list):
		for i in node:
			for x in _values(i, kv):
				yield x
	elif isinstance(node, dict):
		if kv in node:
			yield node[kv]
		for j in node.values():
			for x in _values(j, kv):
				yield x


width: int = 1200
height: int = 600

large_font_bold = ImageFont.truetype("assets/fonts/Roboto-Bold.ttf", 80)
large_font = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 80)
large_font_light = ImageFont.truetype("assets/fonts/Roboto-Light.ttf", 80)

content_font = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 30)
content_font_light = ImageFont.truetype("assets/fonts/Roboto-Light.ttf", 30)


def ticker(symbol: str, data: dict) -> io.BytesIO:
	color = "#2f363d"
	
	image = Image.new("RGB", (width, height), "white")
	draw = ImageDraw.Draw(image)
	
	ticker_length = draw.textlength(f"{symbol} / ", font=large_font_light)
	name_length = draw.textlength(data.get("shortName") or "Name not found", font=large_font_bold)
	
	draw.text((125 + ticker_length, 175), f"{symbol} / ", fill=color, anchor="rs", font=large_font_light)
	
	if ticker_length + name_length + 250 <= width:
		draw.text((125 + ticker_length, 175), data.get("shortName") or "Name not found", fill="#486edb", anchor="ls",
		          font=large_font_bold)
		draw.text((125 + ticker_length, 225), data.get("industry") or "", fill=color, anchor="ls", font=content_font_light)
	else:
		draw.text((125, 255), data.get("shortName") or "Name not found", fill="#486edb", anchor="ls", font=large_font_bold)
		draw.text((125, 300), data["industry"] or "", fill=color, anchor="ls", font=content_font_light)
	
	profile: dict = data.get("profile", {}) or {}
	
	draw.text((125, 410), "Country", fill=color, anchor="ls", font=content_font)
	draw.text((125, 450), profile.get("country", None) or "No data", fill=color, anchor="ls", font=content_font_light)
	
	draw.text((350, 410), "Employees", fill=color, anchor="ls", font=content_font)
	draw.text((350, 450), str(profile.get("fullTimeEmployees", None) or "No data") or "No data", fill=color, anchor="ls",
	          font=content_font_light)
	
	draw.text((575, 410), "CEO", fill=color, anchor="ls", font=content_font)
	
	ceo = profile.get("companyOfficers", [])[0].get("name", None) if profile.get("companyOfficers", []) else None
	draw.text((575, 450), ceo or "No data", fill=color, anchor="ls",
	          font=content_font_light)
	
	colors = [value for value in _values(data, "color")]
	
	line_length = width / len(colors)
	line_pos = 0
	for color in colors:
		draw.line(((line_pos, height), (line_pos + line_length, height)), fill=color, width=50)
		line_pos += line_length
	
	img_io = io.BytesIO()
	image.save(img_io, 'jpeg', quality=70)
	img_io.seek(0)
	
	return img_io


def error(code: int, description: str) -> io.BytesIO:
	
	font_bold = ImageFont.truetype("assets/fonts/Roboto-Bold.ttf", 100)
	font_light = ImageFont.truetype("assets/fonts/Roboto-Light.ttf", 100)
	
	color = "#701516"
	image = Image.new("RGB", (width, height), "white")
	draw = ImageDraw.Draw(image)
	
	code_length = draw.textlength(f"{code} / ", font=large_font_light)
	
	draw.text((125 + code_length, height / 2), f"{code} / ", fill=color, anchor="rs", font=font_light)
	draw.text((125 + code_length, height / 2), description, fill="#2f363d", anchor="ls", font=font_bold)
	
	draw.line(((0, height), (width, height)), fill=color, width=50)
	
	img_io = io.BytesIO()
	image.save(img_io, 'jpeg', quality=70)
	img_io.seek(0)
	
	return img_io
