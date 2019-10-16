# THIS IS PSEUDO CODE AND NEEDS REVIEWING
# attest_data the attestation data corresponding to the attestation we're evaluating
# attestation_history is a vector of ValidatorHistoricalAttestation structs

def check_inner_attestations(attest_data, history_before_attest_target):
    inner_attestations = []
    # creating a list of attestations contained between SOURCE and TARGET of attestation
    for prev_attest in history_before_attest_target:
        if prev_attest.target_epoch <= attest_data.source.epoch:
            break
        inner_attestations.append(prev_attest)
    # checking if we're surrounding a vote
    for challenger_data in inner_attestations:
        if challenger_data.source_epoch > attest_data.source.epoch:
            # we'd be surrounding a vote! SLASHABLE!
            return False
    return True

def check_outer_attestations(attest_data, history_after_attest_target):
    for next_attest in history_after_attest_target:
        if next_attest.source_epoch < attest_data.source.epoch:
            # we'd be inserting a surrounded vote! SLASHABLE!
            return False
    return True

def check_attest_validity(attest_data):
    if attest_data.target.epoch <= attest_data.source.epoch:
        return False
    return True

def should_sign_attestation(attest_data, attestation_history):
    if not check_attest_validity(attest_data):
        print("invalid data!")
        return False
    target_in_history = False
    target_index = len(attestation_history) - 1
    for (index, prev_attest) in enumerate(attestation_history[::-1]):
        if prev_attest.target_epoch <= attest_data.target.epoch:
            target_index = len(attestation_history) - index - 1
            target_in_history = True
            break
    if not target_in_history:
        if len(attestation_history) == 0:
            # history is empty
            print("history is empty")
            return True
        else:
            # pruning error in DB?
            print("pruning error?")
            return False
    corresponding_data = attestation_history[target_index]
    # to_bytes is probably wrong here but the goal is just to compare hashes
    # this condition is not checked earlier because it shouldn't happen often in practice
    if corresponding_data.preimage_hash == attest_data.hash256:
        # it's the same vote
        print("same vote")
        return True
    elif corresponding_data.target_epoch == attest_data.target.epoch:
        # double vote! SLASHABLE!
        print("double vote")
        return False
    else:
        # check that we're not surrounding any vote
        if check_inner_attestations(attest_data, attestation_history[target_index::-1]) == False:
            print("surrounding")
            return False
        # check that we're not inserting a surrounded vote
        if target_index == len(attestation_history) - 1:
            # the attestation_data target epoch is bigger than any target in history: we're not inserting a surrounded vote
            print("target is higher")
            return True
        if check_outer_attestations(attest_data, attestation_history[target_index + 1::]) == False:
            print("surrounded")
            return False
    print("all ok")
    return True

class source:
    def __init__(self, epoch):
        self.epoch = epoch

class target:
    def __init__(self, epoch):
        self.epoch = epoch

class attestation_data:
    def __init__(self, source_epoch, target_epoch, hash256):
        self.source = source(source_epoch)
        self.target = target(target_epoch)
        # this would not be a field but rather something like .hash() or to_bytes()
        self.hash256 = hash256
    
    def print(self):
        print("Source Epoch: ", self.source.epoch)
        print("Target Epoch: ", self.target.epoch)
        print("Hash:         ", self.hash256)

class historical_attestation:
    def __init__(self, source_epoch, target_epoch, hash256):
        self.source_epoch = source_epoch
        self.target_epoch = target_epoch
        self.preimage_hash = hash256

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
