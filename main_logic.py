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