from lib import *
from main_logic import *

attestation_history = [
        historical_attestation(0, 1, "ewq231"),
        historical_attestation(1, 2, "dsadsa"),
        historical_attestation(1, 3, "oiu321"),
        historical_attestation(3, 4, "213720"),
        historical_attestation(3, 6, "q321ulkj"),
        ]

attest_data = attestation_data(0, 1, "ewq231")
print("Empty history test")
assert(should_sign_attestation(attest_data, [])[0] == True), "Empty history should be ok"
print("Ok ✅")

attest_data = attestation_data(0, 1, "ewq231")
print("Same vote test")
assert(should_sign_attestation(attest_data, attestation_history)[0] == True), "Same vote should be ok"
print("Ok ✅")

attest_data = attestation_data(0, 1, "ewqlkjw213")
print("Double vote")
assert(should_sign_attestation(attest_data, attestation_history)[0] == False), "two attestations with same target epoch is a double vote"
print("Ok ✅")

attest_data = attestation_data(3, 7, "qewqk132")
print("Valid vote")
assert(should_sign_attestation(attest_data, attestation_history)[0] == True), "valid vote"
print("Ok ✅")

attest_data = attestation_data(0, 7, "qlkj21")
print("Surround multiple attestations vote")
assert(should_sign_attestation(attest_data, attestation_history)[0] == False), "surrounding lots of votes"
print("Ok ✅")

attest_data = attestation_data(4, 5, "qlkj21")
print("Surround one vote")
assert(should_sign_attestation(attest_data, attestation_history)[0] == False), "getting surrounded by one vote"
print("Ok ✅")

attestation_history = [
        historical_attestation(0, 3, "eqwedsa"),
        historical_attestation(3, 6, "qelkj1"),
        historical_attestation(6, 9, "qesa21")
        ]

attest_data = attestation_data(1, 4, "epoia")
print("Valid interlaced vote")
assert(should_sign_attestation(attest_data, attestation_history)[0] == True), "valid interlaced vote"
print("Ok ✅")

attest_data = attestation_data(1, 5, "epoia")
print("Valid interlaced vote")
assert(should_sign_attestation(attest_data, attestation_history)[0] == True), "valid interlaced vote"
print("Ok ✅")

attest_data = attestation_data(1, 6, "epoia")
print("Double vote")
assert(should_sign_attestation(attest_data, attestation_history)[0] == False), "double vote"
print("Ok ✅")

attest_data = attestation_data(5, 5, "epoia")
print("Target equal to source")
assert(should_sign_attestation(attest_data, attestation_history)[0] == False), "invalid data"
print("Ok ✅")

attest_data = attestation_data(6, 5, "epoia")
print("Target smaller than source")
assert(should_sign_attestation(attest_data, attestation_history)[0] == False), "invalid data"
print("Ok ✅")

attestation_history = [
        historical_attestation(3, 6, "qelkj1"),
        historical_attestation(6, 9, "qesa21")
        ]

attest_data = attestation_data(0, 3, "epoia")
print("Pruned history")
assert(should_sign_attestation(attest_data, attestation_history)[0] == False), "bad pruning"
print("Ok ✅")
