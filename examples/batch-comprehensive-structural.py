#!/usr/bin/env python3
import os
import uuid
import json
import http.client
import sys
import csv
from urllib.parse import urlparse


def make_request(method, path, data, token, host):
	parsed = urlparse(host)
	conn = http.client.HTTPSConnection(parsed.netloc)
	headers = {"Content-Type": "application/json", "Authorization": f"Basic {token}"}
	conn.request(method, f"/v1/structural/{path}", data, headers)
	return conn.getresponse()


def read_addresses(csv_path):
	addresses = []
	with open(csv_path, "r") as f:
		reader = csv.DictReader(f)
		if "address" not in reader.fieldnames:
			raise ValueError("CSV must contain an 'address' column")
		for row in reader:
			addresses.append(row["address"])
	return addresses


def main():
	if len(sys.argv) < 2:
		print("Usage: batch-comprehensive-structural-residential.py <input.csv>")
		sys.exit(1)

	token = os.getenv("TOKEN")
	if not token:
		print("please set the TOKEN environment variable")
		sys.exit(1)

	host = os.getenv("API_HOST", "https://api.climaterisk.qa")

	try:
		addresses = read_addresses(sys.argv[1])
	except Exception as e:
		print(f"Error reading CSV: {e}")
		sys.exit(1)

	# Generate new UUIDs
	ids = [str(uuid.uuid4()) for _ in addresses]
	ids_json = json.dumps(ids)

	# Batch request
	print("\n\n/batch response:")
	batch_data = "\n".join(
		[
			json.dumps({"item_id": id_, "geocoding": {"address": addr}})
			for id_, addr in zip(ids, addresses)
		]
	)

	resp = make_request("POST", "simple/residential/batch", batch_data, token, host)
	print(resp.read().decode())

	# Progress request
	print("\n\n/progress response - note the streaming:")
	resp = make_request("POST", "simple/residential/progress", ids_json, token, host)
	while True:
		chunk = resp.read(1)
		if not chunk:
			break
		if chunk != b"\x1e":  # Skip record separator
			sys.stdout.buffer.write(chunk)
			sys.stdout.buffer.flush()

	# Results retrieval
	print("\n\n/results retrieval:")
	resp = make_request("POST", "comprehensive/results", ids_json, token, host)
	results = []

	# Read response and remove record separators
	data = resp.read().decode("utf-8")
	for line in data.split("\x1e"):
		if line.strip():
			results.append(line)

	# Save as JSONL file
	with open("results.jsonl", "w") as f:
		for line in results:
			f.write(line + "\n")

	print("\n\nresults saved to results.jsonl")

	# Print parsed results
	try:
		for line in results:
			parsed = json.loads(line)
			print(json.dumps(parsed, indent=2))
	except json.JSONDecodeError:
		print("Could not parse results as JSON")


if __name__ == "__main__":
	main()
