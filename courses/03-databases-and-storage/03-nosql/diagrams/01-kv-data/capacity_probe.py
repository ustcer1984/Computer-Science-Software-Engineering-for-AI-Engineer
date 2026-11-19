"""§4 — capacity-unit accounting, read back from DynamoDB Local with ReturnConsumedCapacity=TOTAL.

Writes items of 0.5, 1, 1.5 and 5 KB; reads one 5 KB item eventually and strongly consistent; scans the table; checks
that a 401 KB item is rejected (the 400 KB item limit) and what a failed conditional write and a 2-item transaction
consume.

Usage:  python capacity_probe.py <dynamodb-endpoint>  > capacity-out.txt
"""
import sys, boto3

d = boto3.client("dynamodb", endpoint_url=sys.argv[1], region_name="ap-southeast-1",
                 aws_access_key_id="local", aws_secret_access_key="local")
try: d.delete_table(TableName="cap")
except d.exceptions.ResourceNotFoundException: pass
d.create_table(TableName="cap", BillingMode="PAY_PER_REQUEST", KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
               AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}])
cc = lambda r: r["ConsumedCapacity"]["CapacityUnits"]
for name, size in (("i500", 500), ("i1k", 1000), ("i1500", 1500), ("i5k", 5000)):
    r = d.put_item(TableName="cap", Item={"pk": {"S": name}, "v": {"S": "x" * size}}, ReturnConsumedCapacity="TOTAL")
    print(f"PutItem {size:>5}-byte value: {cc(r)} write units")
print("GetItem 5 KB, eventually consistent:", cc(d.get_item(TableName="cap", Key={"pk": {"S": "i5k"}}, ReturnConsumedCapacity="TOTAL")), "read units")
print("GetItem 5 KB, strongly consistent:  ", cc(d.get_item(TableName="cap", Key={"pk": {"S": "i5k"}}, ConsistentRead=True, ReturnConsumedCapacity="TOTAL")), "read units")
print("GetItem of a key that does not exist:", cc(d.get_item(TableName="cap", Key={"pk": {"S": "nope"}}, ReturnConsumedCapacity="TOTAL")), "read units")
r = d.scan(TableName="cap", ReturnConsumedCapacity="TOTAL")
print(f"Scan of the 4 items (8 KB in total): {cc(r)} read units, Count {r['Count']}")
try:
    d.put_item(TableName="cap", Item={"pk": {"S": "big"}, "v": {"S": "x" * (401 * 1024)}})
except Exception as e:
    print("PutItem 401 KB:", type(e).__name__, "-", str(e).split(": ", 1)[-1])
try:
    d.put_item(TableName="cap", Item={"pk": {"S": "i1k"}, "v": {"S": "y"}}, ConditionExpression="attribute_not_exists(pk)",
               ReturnConsumedCapacity="TOTAL")
except d.exceptions.ConditionalCheckFailedException as e:
    print("Conditional PutItem that failed (attribute_not_exists on an existing key): ConditionalCheckFailedException")
r = d.transact_write_items(TransactItems=[{"Put": {"TableName": "cap", "Item": {"pk": {"S": "t1"}, "v": {"S": "a"}}}},
                                          {"Put": {"TableName": "cap", "Item": {"pk": {"S": "t2"}, "v": {"S": "b"}}}}],
                           ReturnConsumedCapacity="TOTAL")
print("TransactWriteItems, 2 small items:", r["ConsumedCapacity"][0]["CapacityUnits"], "write units")
try:
    d.transact_write_items(TransactItems=[{"Put": {"TableName": "cap", "Item": {"pk": {"S": f"x{i}"}}}} for i in range(101)])
except Exception as e:
    print("TransactWriteItems with 101 items:", type(e).__name__, "-", str(e).split(": ", 1)[-1][:160])
