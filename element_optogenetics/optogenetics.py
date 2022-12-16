import inspect
import importlib
import datajoint as dj

schema = dj.Schema()


def activate(
    schema_name: str,
    *,
    create_schema: bool = True,
    create_tables: bool = True,
    linking_module: bool = None
):
    """Activate this schema.

    Args:
        schema_name (str): schema name on the database server
        create_schema (bool): when True (default), create schema in the database if it
                            does not yet exist.
        create_tables (bool): when True (default), create schema tables in the database
                             if they do not yet exist.
        linking_module (str): a module (or name) containing the required dependencies.

    Dependencies:
        Upstream tables:
            Device: Referenced by OptoProtocol. Device to perform procedure
            Session: Referenced by OptoProtocol. Typically a recording session
            Implantation: Referenced by OptoProtocol. A surgery for opto fiber.
    """

    if isinstance(linking_module, str):
        linking_module = importlib.import_module(linking_module)
    assert inspect.ismodule(
        linking_module
    ), "The argument 'linking_module' must be a module's name or a module"

    global _linking_module
    _linking_module = linking_module

    schema.activate(
        schema_name,
        create_schema=create_schema,
        create_tables=create_tables,
        add_objects=_linking_module.__dict__,
    )


@schema
class OptoWaveformType(dj.Lookup):
    """Stimulus waveform type (e.g., square, sine, etc.)

    Attributes:
        waveform_type ( varchar(32) ): Waveform type (e.g., square, sine)
    """

    definition = """
    waveform_type:    varchar(32)
    """
    contents = zip(["Square", "Ramp", "Sine"])


@schema
class OptoWaveform(dj.Lookup):
    """OptoWaveform defines the shape of one cycle of the optogenetic stimulus

    Child tables specify features of specific waveforms (e.g., square, sine, etc.)

    Attributes:
        waveform_name ( varchar(32) ): Name of waveform
        OptoWaveformType (foreign key): OptoWaveformType primary key
        normalized_waveform (longblob, nullable): For one cycle, normalized to peak
        waveform_description ( varchar(255), nullable ): Description of waveform
    """

    definition = """
    # OptoWaveform defines the shape of one cycle of the optogenetic stimulus
    waveform_name            : varchar(32)
    ---
    -> OptoWaveformType
    normalized_waveform=null : longblob      # For one cycle, normalized to peak
    waveform_description=''  : varchar(255)  # description of the waveform
    """

    class Square(dj.Part):
        """Square waveform

        Attributes:
            OptoWaveform (foreign key): OptoWaveform primary key
            on_proportion ( decimal(2, 2) ): Proportion of stim on time within a cycle
            off_proportion ( decimal(2, 2) ): Proportion of stim off time within a cycle
        """

        definition = """
        -> master
        ---
        on_proportion  : decimal(2, 2) # prop of stim on time within a cycle
        off_proportion : decimal(2, 2) # prop of stim off time within a cycle
        """

    class Ramp(dj.Part):
        """Ramp waveform

        Attributes:
            OptoWaveform (foreign key): OptoWaveform primary key
            ramp_up_proportion ( decimal(2, 2) ): Ramp up proportion of the linear waveform
            ramp_down_proportion ( decimal(2, 2) ): Ramp down proportion of the linear waveform
        """

        definition = """
        -> master
        ---
        ramp_up_proportion   : decimal(2, 2) # ramp up prop of the linear waveform
        ramp_down_proportion : decimal(2, 2) # ramp down prop of the linear waveform
        """

    class Sine(dj.Part):
        """Sine Waveform. Starting_phase ranges (0, 2]. 0 for Sine, 0.5 for Cosine

        Attributes:
            OptoWaveform (foreign key): OptoWaveform primary key
            number_of_cycles (smallint): Number of cycles
            starting_phase (decimal(3, 2) ): Phase in pi at the beginning of the cycle.
                Defaults to 0
        """

        definition = """ # Starting_phase ranges (0, 2]. 0 for Sine, 0.5 for Cosine
        -> master
        ---
        number_of_cycles  : smallint
        starting_phase=0  : decimal(3, 2) # (pi) phase at the beginning of the cycle
        """


@schema
class OptoStimParams(dj.Manual):
    """A single opto stimulus that repeats

    Power and intensity are both nullable. Users may wish to document one or the other.

    Attributes:
        opto_params_id (smallint): Stimulus parameter ID
        OptoWaveform (foreign key): OptoWaveform primary key
        Device (foreign key): Device primary key
        wavelength (smallint): Wavelength in nm of photo stim. light
        power ( decimal(6, 2), nullable ): Total power in mW from light source
        intensity ( decimal(6, 2), nullable ): Power for given area
        frequency ( decimal(5, 1) ): Frequency in Hz of the waveform
        duration ( decimal(5, 1) ): Duration in ms of each optostimulus
        protocol_description ( varchar(255) ): Protocol description
    """

    definition = """
    # Defines a single opto stimulus that repeats
    opto_params_id     : smallint
    ---
    -> OptoWaveform
    wavelength           : int             # (nm) wavelength of photo stim. light
    power=null           : decimal(6, 2)   # (mW) total power from light source
    light_intensity=null : decimal(6, 2)   # (mW/mm2) light intensity
    frequency            : decimal(5, 1)   # (Hz) frequency of the waveform
    duration             : decimal(5, 1)   # (ms) duration of each opto stimulus
    protocol_description='' : varchar(255) # description of optogenetics protocol
    """


@schema
class OptoProtocol(dj.Manual):
    """Protocol for a given session, applying a simulus to an implantation via a device

    Attributes:
        protocol_id (int): Protocol ID
        Session (foreign key): Session primary key
        OptoStimParams (foreign key): OptoStimParams primary key
        Implantation (foreign key): Implantation primary key
        Device  (foreign key, nullable): Device  primary key
    """

    definition = """
    -> Session
    protocol_id: int
    ---
    -> OptoStimParams
    -> Implantation
    -> [nullable] Device
    """


@schema
class OptoEvent(dj.Manual):
    """Event within a session

    WRT: with respect to

    Attributes:
        OptoProtocol (foreign key): OptoProtocol primary key
        stim_start_time (float): Stimulus start time in seconds wrt session start
        stim_end_time (float): Stimulus end time in seconds wrt session start
    """

    definition = """
    -> OptoProtocol
    stim_start_time  : float  # (s) opto stimulus start time wrt session start
    ---
    stim_end_time    : float  # (s) opto stimulus end time wrt session start
    """
