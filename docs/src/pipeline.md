# Data Pipeline

Each node in the following diagram represents the analysis code in the workflow and the
corresponding tables in the database.  Within the workflow, Element Optogenetics connects
to upstream Elements including Lab, Animal, and Session.  For more detailed
documentation on each table, see the API docs for the respective schemas.

![pipeline](https://raw.githubusercontent.com/datajoint/element-optogenetics/main/images/pipeline.svg)

## `reference` schema ([API docs](https://datajoint.com/docs/elements/element-optogenetics/latest/api/workflow_optogenetics/reference))

| Table | Description |
| --- | --- |
| Device | Pulse generator device |

## `subject` schema ([API docs](https://docs.datajoint.com/elements/element-animal/latest/api/element_animal/subject/))

- Although not required, most choose to connect the `Session` table to a `Subject` table.

| Table | Description |
| --- | --- |
| Subject | Basic information of the research subject |

## `surgery` schema ([API docs](https://datajoint.com/docs/elements/element-animal/latest/api/element_animal/surgery/#element_animal.surgery.Implantation))

- The `Implantation` table can be user-defined , or one can choose to use the `surgery.Implantation` table from `element-animal`.

| Table | Description |
| --- | --- |
| Implantation | Location of an implanted device |

## `session` schema ([API docs](https://docs.datajoint.com/elements/element-session/latest/api/element_session/session_with_id/))

| Table | Description |
| --- | --- |
| Session | Unique experimental session identifier |

## `optogenetics` schema ([API docs](https://datajoint.com/docs/elements/element-optogenetics/latest/api/element_optogenetics/optogenetics))

| Table               | Description |
| ---                 |   ---       |
| OptoWaveformType | Stimulus waveform type (e.g., square, ramp, sine) |
| OptoWaveform | Shape of one cycle of the stimulus waveform |
| OptoWaveform.Square | Square waveform properties |
| OptoWaveform.Ramp | Ramp waveform properties |
| OptoWaveform.Sine | Sine waveform properties |
| OptoStimParams | Stimulus parameters |
| OptoProtocol | Protocol for a given session |
| OptoEvent | Start and end time of the stimulus within a session |
