"""
Seeding and configuration utilities for reproducibility.
Handles random seed initialization and environment configuration.
"""

import os
import random
import numpy as np
import tensorflow as tf
import torch
from typing import Optional


def set_random_seed(seed: int = 42) -> None:
    """
    Set random seeds for reproducibility across all libraries.

    Call this function at the start of your script to ensure
    reproducible results across runs.

    Parameters:
    -----------
    seed : int, default=42
        Random seed value
    """
    # Python random
    random.seed(seed)

    # NumPy random
    np.random.seed(seed)

    # TensorFlow (if installed)
    try:
        tf.random.set_seed(seed)
        tf.compat.v1.set_random_seed(seed)
    except Exception:
        pass

    # PyTorch (if installed)
    try:
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        pass

    # Environment variables for additional reproducibility
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1'


def get_seed() -> int:
    """
    Get the current random seed value.

    Returns:
    --------
    int
        Current seed value (default is 42 if not explicitly set)
    """
    return getattr(get_seed, '_seed', 42)


def configure_environment(seed: int = 42,
                          gpu_memory_fraction: Optional[float] = None,
                          verbose: bool = True) -> dict:
    """
    Configure the environment for reproducible ML experiments.

    Parameters:
    -----------
    seed : int, default=42
        Random seed for reproducibility
    gpu_memory_fraction : float, optional
        Fraction of GPU memory to allocate (0.0 to 1.0)
        If None, uses TensorFlow's default dynamic memory allocation
    verbose : bool, default=True
        Whether to print configuration details

    Returns:
    --------
    dict
        Configuration details applied
    """
    config = {
        'seed': seed,
        'gpu_enabled': torch.cuda.is_available() if torch.cuda else False,
        'numpy_version': np.__version__,
    }

    # Set seed
    set_random_seed(seed)

    # Configure GPU memory (TensorFlow)
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus and gpu_memory_fraction:
            for gpu in gpus:
                tf.config.set_logical_device_configuration(
                    gpu,
                    [tf.config.LogicalDeviceConfiguration(
                        memory_limit=int(gpu_memory_fraction * 1024)
                    )]
                )
                config['gpu_memory_limit'] = gpu_memory_fraction
    except Exception:
        pass

    if verbose:
        print("Environment Configuration:")
        print(f"  Random Seed: {seed}")
        print(f"  GPU Available (PyTorch): {config['gpu_enabled']}")
        if 'gpu_memory_limit' in config:
            print(f"  GPU Memory Fraction: {config['gpu_memory_limit']}")
        print(f"  NumPy Version: {config['numpy_version']}")

    return config


class SeedManager:
    """
    Manager class for handling random seeds and reproducibility
    across multiple experiments or runs.
    """

    _instance = None
    _seed = 42

    def __new__(cls):
        """Singleton pattern for SeedManager."""
        if cls._instance is None:
            cls._instance = super(SeedManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the seed manager."""
        self._seed = 42
        self._experiment_seeds = {}

    def set_seed(self, seed: int) -> None:
        """
        Set the global random seed.

        Parameters:
        -----------
        seed : int
            Random seed value
        """
        self._seed = seed
        set_random_seed(seed)

    def get_seed(self) -> int:
        """Get the current global seed."""
        return self._seed

    def create_experiment_seed(self, experiment_name: str) -> int:
        """
        Create a deterministic seed for an experiment.

        Parameters:
        -----------
        experiment_name : str
            Name of the experiment

        Returns:
        --------
        int
            Generated seed for the experiment
        """
        # Create a hash-based seed from experiment name and base seed
        experiment_seed = (
                hash(f"{experiment_name}_{self._seed}") % (2 ** 32 - 1)
        )
        self._experiment_seeds[experiment_name] = experiment_seed
        return experiment_seed

    def get_experiment_seed(self, experiment_name: str) -> int:
        """Get seed for a specific experiment."""
        return self._experiment_seeds.get(
            experiment_name,
            self.create_experiment_seed(experiment_name)
        )

    def reset(self) -> None:
        """Reset all seeds to default."""
        self._seed = 42
        self._experiment_seeds.clear()
        set_random_seed(42)


def set_numpy_seed(seed: int = 42) -> None:
    """
    Set only NumPy random seed.

    Parameters:
    -----------
    seed : int, default=42
        Random seed value
    """
    np.random.seed(seed)


def set_torch_seed(seed: int = 42) -> None:
    """
    Set only PyTorch random seeds.

    Parameters:
    -----------
    seed : int, default=42
        Random seed value
    """
    try:
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
    except Exception:
        pass


def set_tensorflow_seed(seed: int = 42) -> None:
    """
    Set only TensorFlow random seed.

    Parameters:
    -----------
    seed : int, default=42
        Random seed value
    """
    try:
        tf.random.set_seed(seed)
        tf.compat.v1.set_random_seed(seed)
    except Exception:
        pass


def get_reproducible_config() -> dict:
    """
    Get current reproducibility configuration.

    Returns:
    --------
    dict
        Configuration with seed and framework availability
    """
    return {
        'seed': SeedManager().get_seed(),
        'torch_available': True,
        'tensorflow_available': True,
        'numpy_available': True,
        'python_hashseed': os.environ.get('PYTHONHASHSEED', 'not set'),
        'deterministic_ops': os.environ.get('TF_DETERMINISTIC_OPS', 'not set'),
    }