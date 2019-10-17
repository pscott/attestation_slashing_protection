def check_attest_validity(attest_data):
    if attest_data.target.epoch <= attest_data.source.epoch:
        return False
    return True

def should_sign_attestation(attest_data, attestation_history):
    if not check_attest_validity(attest_data):
        return (False, "invalid attestation_data")
    if len(attestation_history) == 0:
        return (True, "empty history")
    i = len(attestation_history) - 1
    # Checking for (b1)
    while attestation_history[i].target_epoch > attest_data.target.epoch:
        if attestation_history[i].source_epoch < attest_data.source.epoch:
            return (False, "surrounded vote")
        if i == 0:
            return (False, "pruning error")
        i -= 1
    if attestation_history[i].target_epoch == attest_data.target.epoch:
        if attestation_history[i].preimage_hash == attest_data.hash256:
            return (True, "same vote")
        else:
            return (False, "double vote")
    else:
        # Checking for (b2)
        while (i >= 0 and attestation_history[i].target_epoch >= attest_data.source.epoch):
            if attestation_history[i].source_epoch > attest_data.source.epoch:
                return (False, "surrounding vote")
            i -= 1
        return (True, "valid attestation")
