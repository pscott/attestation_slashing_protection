# attestation_slashing_protection
Small PoC to protect a validator client from signing slashable attestations

Please read https://hackmd.io/u8MTIe5IRmybzVz38-sGdQ for more context.

To run the tests, clone the repository and run `python3 tests.py`
You can edit the tests in `tests.py`

Here's the idea:
  1. Find the first target epoch that is smaller or equal to the attestation target epoch. If it is equal, check that their hashes are the same, else return false.
  2. Then, check that we are not surrounding any previous attestations by creating a list that contains every historical_attestation that has a target_epoch that is between current_attestation.source.epoch and current_attestation.target.epoch, and checking that no element in this list has a source_epoch that is higher than current_attestaion.target.epoch
  3. Then, check that we are not inserting a surrounded attestation by creating another list that contains all historical_attestations that have a target higher than the curr_attestation.target.epoch and checking that no element in this list has a source_epoch that is smaller than the current_attestation.source.epoch.

For this PoC, we're allocating multiple lists, but in reality we could just use one list and just play with indeces for extra performance (we need to be extra careful with segv though).

By taking advantage of the fact that the attestation_history is already sorted, this algorithm should be near instantaneous in almost all normal cases. The complexity is a linear function of the number of target epochs in the attestation_history that are bigger than the `current_attestation.source.epoch`
