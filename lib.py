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
    
    def print(self):
        print("Source_epoch: ", self.source_epoch)
        print("Target_epoch: ", self.target_epoch)
        print("Hash:         ", self.preimage_hash)

