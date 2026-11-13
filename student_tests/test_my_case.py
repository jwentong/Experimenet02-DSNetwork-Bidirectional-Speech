import numpy as np
import pytest

from src.t_switch import t_switch


def test_t_switch_rejects_wrong_frame_shape_without_mutation():
    frame = np.zeros((2, 32), dtype=np.uint8)
    original = frame.copy()

    with pytest.raises(ValueError):
        t_switch(frame, {})

    assert np.array_equal(frame, original)