import json

def save(sections_name, json_file):
	d = {}
	d['sections_name'] = sections_name
	with open(json_file, 'w') as f:
		json.dump(d, f)

def load(json_file):
	with open(json_file, 'r') as f:
		d = json.load(f)

	return d['sections_name']

