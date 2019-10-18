#[derive(PartialEq, Default, Debug, Clone)]
pub struct Checkpoint {
    epoch: u64,
}

impl Checkpoint {
    fn new(epoch: u64) -> Self {
        Checkpoint { epoch }
    }
}

#[derive(Default, Debug)]
pub struct AttestationData {
    source: Checkpoint,
    target: Checkpoint,
    hash256: String,
}

impl AttestationData {
    fn new(source_epoch: u64, target_epoch: u64, preimage_hash: &str) -> Self {
        AttestationData {
            source: Checkpoint::new(source_epoch),
            target: Checkpoint::new(target_epoch),
            hash256: String::from(preimage_hash),
        }
    }
}

#[derive(Default, Debug)]
pub struct ValidatorHistoricalAttestation {
    source_epoch: u64,
    target_epoch: u64,
    preimage_hash: String,
}

impl ValidatorHistoricalAttestation {
    fn new(source_epoch: u64, target_epoch: u64, preimage_hash: &str) -> Self {
        ValidatorHistoricalAttestation {
            source_epoch,
            target_epoch,
            preimage_hash: String::from(preimage_hash),
        }
    }
}

#[derive(PartialEq, Debug)]
pub enum PruningError {
    TargetEpochTooSmall(u64),
    SourceEpochTooSmall(u64),
}

#[derive(PartialEq, Debug)]
pub enum AttestationError {
    DoubleVote,
    InvalidAttestationData {
        source: Checkpoint,
        target: Checkpoint,
    },
    PruningError(PruningError),
    Surrounded,
    Surrounding,
}

#[derive(PartialEq, Debug)]
pub enum ValidAttestation {
    EmptyHistory,
    SameVote,
    ValidAttestation,
}

fn check_attestation_validity(attestation_data: &AttestationData) -> Result<(), AttestationError> {
    if attestation_data.target.epoch <= attestation_data.source.epoch {
        Err(AttestationError::InvalidAttestationData {
            source: attestation_data.source.clone(),
            target: attestation_data.target.clone(),
        })
    } else {
        Ok(())
    }
}

fn check_surrounded(
    attestation_data: &AttestationData,
    attestation_history: &[ValidatorHistoricalAttestation],
) -> Result<(), AttestationError> {
    let surrounded = attestation_history.iter().any(|historical_attestation| {
        historical_attestation.source_epoch < attestation_data.source.epoch
    });
    if surrounded {
        Err(AttestationError::Surrounded)
    } else {
        Ok(())
    }
}

fn check_surrounding(
    attestation_data: &AttestationData,
    attestation_history: &[ValidatorHistoricalAttestation],
) -> Result<(), AttestationError> {
    let surrounding = attestation_history.iter().any(|historical_attestation| {
        historical_attestation.source_epoch > attestation_data.source.epoch
    });
    if surrounding {
        Err(AttestationError::Surrounding)
    } else {
        Ok(())
    }
}

fn should_sign_attestation(
    attestation_data: &AttestationData,
    attestation_history: &[ValidatorHistoricalAttestation],
) -> Result<(ValidAttestation), AttestationError> {
    check_attestation_validity(attestation_data)?;
    if attestation_history.is_empty() {
        return Ok(ValidAttestation::EmptyHistory);
    }

    let target_index = match attestation_history
        .iter()
        .rev()
        .position(|historical_attestation| {
            historical_attestation.target_epoch <= attestation_data.target.epoch
        }) {
        None => {
            return Err(AttestationError::PruningError(
                PruningError::TargetEpochTooSmall(attestation_data.target.epoch),
            ))
        }
        Some(index) => attestation_history.len() - index - 1,
    };

    check_surrounded(attestation_data, &attestation_history[target_index + 1..])?;
    if attestation_history[target_index].target_epoch == attestation_data.target.epoch {
        if attestation_history[target_index].preimage_hash == attestation_data.hash256 {
            return Ok(ValidAttestation::SameVote);
        } else {
            return Err(AttestationError::DoubleVote);
        }
    }

    let source_index =
        match attestation_history[..=target_index]
            .iter()
            .rev()
            .position(|historical_attestation| {
                historical_attestation.target_epoch <= attestation_data.source.epoch
            }) {
            None => {
                if attestation_data.source.epoch == 0 {
                    0 // double check
                } else {
                    return Err(AttestationError::PruningError(
                        PruningError::SourceEpochTooSmall(attestation_data.source.epoch),
                    ));
                }
            }
            Some(index) => target_index - index + 1
        };

    check_surrounding(
        attestation_data,
        &attestation_history[source_index..=target_index],
    )?;

    Ok(ValidAttestation::ValidAttestation)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_simple_test() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 2, "231k"));

        let attestation_data = AttestationData::new(2, 3, "wqpoi2109");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Ok(ValidAttestation::ValidAttestation)
        );
    }

    #[test]
    fn valid_empty_history() {
        let history = vec![];

        let attestation_data = AttestationData::new(2, 3, "wqpoi2109");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Ok(ValidAttestation::EmptyHistory)
        );
    }

    #[test]
    fn valid_casting_same_vote() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 2, "e21a"));

        let attestation_data = AttestationData::new(0, 1, "adsl12");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Ok(ValidAttestation::SameVote)
        );
    }

    #[test]
    fn invalid_double_vote() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 2, "e21a"));

        let attestation_data = AttestationData::new(0, 1, "toto");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::DoubleVote)
        );
    }

    #[test]
    fn invalid_surround_one_vote() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 2, "e21a"));
        history.push(ValidatorHistoricalAttestation::new(2, 3, "e21a"));

        let attestation_data = AttestationData::new(1, 4, "2019a");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );
    }

    #[test]
    fn invalid_surround_one_vote_from_genesis() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 2, "adsl12"));

        let attestation_data = AttestationData::new(0, 3, "2019a");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );
    }

    #[test]
    fn invalid_surround_multiple_votes() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 2, "e21a"));
        history.push(ValidatorHistoricalAttestation::new(2, 3, "21ou09"));

        let attestation_data = AttestationData::new(1, 4, "2019a");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );
    }

    #[test]
    fn invalid_surrounded_by_one_vote() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 6, "109a"));

        let attestation_data = AttestationData::new(2, 3, "titi");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounded)
        );
    }

    #[test]
    fn invalid_surrounded_by_multiple_votes() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "adsl12"));
        history.push(ValidatorHistoricalAttestation::new(1, 6, "109a"));
        history.push(ValidatorHistoricalAttestation::new(2, 5, "09a"));

        let attestation_data = AttestationData::new(3, 4, "titi");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounded)
        );
    }

    #[test]
    fn invalid_surrounded_by_one_vote_from_genesis() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "lkj12"));
        history.push(ValidatorHistoricalAttestation::new(0, 3, "adsl12"));

        let attestation_data = AttestationData::new(1, 2, "tutu");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounded)
        );
    }

    #[test]
    fn invalid_surrounding_last_vote() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "lkj12"));
        history.push(ValidatorHistoricalAttestation::new(0, 2, "mn21"));
        history.push(ValidatorHistoricalAttestation::new(2, 3, "mn21"));
        history.push(ValidatorHistoricalAttestation::new(4, 9, "sahjk8"));
        history.push(ValidatorHistoricalAttestation::new(5, 10, "asjk"));
        history.push(ValidatorHistoricalAttestation::new(6, 11, "lkj21"));

        let attestation_data = AttestationData::new(1, 8, "tutu");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );
    }

    #[test]
    fn invalid_surrounding_first_vote() {
        let mut history = vec![];
        history.push(ValidatorHistoricalAttestation::new(0, 1, "lkj12"));
        history.push(ValidatorHistoricalAttestation::new(0, 2, "lkj12"));
        history.push(ValidatorHistoricalAttestation::new(2, 3, "mn21"));

        let attestation_data = AttestationData::new(1, 4, "tutu");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );
    }


    #[test]
    fn valid_complex_test() {
        let mut history = vec![];

        let attestation_data = AttestationData::new(0, 0, "mb987");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::InvalidAttestationData {
                source: attestation_data.source.clone(),
                target: attestation_data.target.clone(),
            })
        );

        let attestation_data = AttestationData::new(1, 0, "lkj09");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::InvalidAttestationData {
                source: attestation_data.source.clone(),
                target: attestation_data.target.clone(),
            })
        );

        let attestation_data = AttestationData::new(0, 1, "iuy76");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Ok(ValidAttestation::EmptyHistory)
        );

        history.push(ValidatorHistoricalAttestation::new(0, 1, "lkj12"));
        let attestation_data = AttestationData::new(0, 1, "tutu");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::DoubleVote)
        );

        let attestation_data = AttestationData::new(0, 1, "lkj12");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Ok(ValidAttestation::SameVote)
        );

        let attestation_data = AttestationData::new(4, 5, "12lkj");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Ok(ValidAttestation::ValidAttestation)
        );

        history.push(ValidatorHistoricalAttestation::new(1, 2, "sdpi0"));
        let attestation_data = AttestationData::new(0, 3, "lkjdas90");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );

        history.push(ValidatorHistoricalAttestation::new(1, 2, "lkj12"));
        let attestation_data = AttestationData::new(0, 3, "09sa");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );

        history.push(ValidatorHistoricalAttestation::new(2, 8, "lkj12"));
        let attestation_data = AttestationData::new(0, 3, "09sa");
        assert_eq!(
            should_sign_attestation(&attestation_data, &history[..]),
            Err(AttestationError::Surrounding)
        );
    }
}
