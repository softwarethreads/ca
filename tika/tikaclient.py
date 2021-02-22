import tika
tika.initVM()
from tika import parser
parsed = parser.from_file('../data/BuildingPermitDoc.pdf')
print(parsed["metadata"])
print(parsed["content"])