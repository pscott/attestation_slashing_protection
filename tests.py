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
assert(should_sign_attestation(attest_data, []) == True), "Empty history should be ok"

attest_data = attestation_data(0, 1, "ewq231")
assert(should_sign_attestation(attest_data, attestation_history) == True), "Same vote should be ok"

attest_data = attestation_data(0, 1, "ewqlkjw213")
assert(should_sign_attestation(attest_data, attestation_history) == False), "two attestations with same target epoch is a double vote"

attest_data = attestation_data(3, 7, "qewqk132")
assert(should_sign_attestation(attest_data, attestation_history) == True), "valid vote"

attest_data = attestation_data(0, 7, "qlkj21")
assert(should_sign_attestation(attest_data, attestation_history) == False), "surrounding lots of votes"

attest_data = attestation_data(4, 5, "qlkj21")
assert(should_sign_attestation(attest_data, attestation_history) == False), "getting surrounded by one vote"

attestation_history = [
        historical_attestation(0, 3, "eqwedsa"),
        historical_attestation(3, 6, "qelkj1"),
        historical_attestation(6, 9, "qesa21")
        ]

attest_data = attestation_data(1, 4, "epoia")
assert(should_sign_attestation(attest_data, attestation_history) == True), "valid interlaced vote"

attest_data = attestation_data(1, 5, "epoia")
assert(should_sign_attestation(attest_data, attestation_history) == True), "valid interlaced vote"

attest_data = attestation_data(1, 6, "epoia")
assert(should_sign_attestation(attest_data, attestation_history) == False), "double vote"

attest_data = attestation_data(5, 5, "epoia")
assert(should_sign_attestation(attest_data, attestation_history) == False), "invalid data"

attest_data = attestation_data(6, 5, "epoia")
assert(should_sign_attestation(attest_data, attestation_history) == False), "invalid data"

attestation_history = [
        historical_attestation(3, 6, "qelkj1"),
        historical_attestation(6, 9, "qesa21")
        ]

attest_data = attestation_data(0, 3, "epoia")
assert(should_sign_attestation(attest_data, attestation_history) == False), "bad pruning"
