import torch
import torch.nn as nn
from torch.nn import functional as F
from typing import Union, Tuple, Iterable


def get_activation_function_from_string(
        activation_name: str
):
    """
    Returns an activation function, based on the name provided.

    :param activation_name: str
        name of the activation function, one of {'elu', 'relu', 'leaky_rely'}
    :return: function
        corresponding activation function
    """
    if activation_name.lower() == 'elu':
        return F.elu
    elif activation_name.lower() == 'relu':
        return F.relu
    elif activation_name.lower() == 'leaky_relu':
        return F.leaky_relu
    else:
        raise ValueError('Invalid activation function.')


def forward_pass_with_unpacked_tuple(
        model: nn.Module,
        x: Union[Tuple, torch.Tensor],
):
    """
    Performs forward pass of model with input x. If x is a tuple, it return
    y = model(*x), else it returns y = model(x).
    :param model: nn.Module
        model for forward pass
    :param x: Union[Tuple, torch.Tensor]
        input for forward pass
    :return: torch.Tensor
        output of the forward pass, either model(*x) or model(x)
    """
    if isinstance(x, Tuple):
        return model(*x)
    else:
        return model(x)


def get_number_of_model_parameters(
        model: nn.Module,
        requires_grad_flags: tuple = (True, False),
):
    """
    Counts parameters of the module. The list requires_grad_flag can be used
    to specify whether all parameters should be counted, or only those with
    requires_grad = True or False.
    :param model: nn.Module
        model
    :param requires_grad_flags: tuple
        tuple of bools, for requested requires_grad flags
    :return:
        number of parameters of the model with requested required_grad flags
    """
    num_params = 0
    for p in list(model.parameters()):
        if p.requires_grad in requires_grad_flags:
            n = 1
            for s in list(p.size()):
                n = n * s
            num_params += n
    return num_params


def get_optimizer_from_kwargs(model_parameters: Iterable,
                              **optimizer_kwargs,
                              ):
    """
    Builds and returns an optimizer for model_parameters. The type of the
    optimizer is determined by kwarg type, the remaining kwargs are passed to
    the optimizer.

    Parameters
    ----------
    model_parameters: Iterable
        iterable of parameters to optimize or dicts defining parameter groups
    optimizer_kwargs:
        kwargs for optimizer; type needs to be one of [adagrad, adam, adamw,
        lbfgs, RMSprop, sgd], the remaining kwargs are used for specific
        optimizer kwargs, such as learning rate and momentum

    Returns
    -------
    optimizer
    """
    optimizers_dict = {
        'adagrad': torch.optim.Adagrad,
        'adam': torch.optim.Adam,
        'adamw': torch.optim.AdamW,
        'lbfgs': torch.optim.LBFGS,
        'RMSprop': torch.optim.RMSprop,
        'sgd': torch.optim.SGD,
    }
    if not 'type' in optimizer_kwargs:
        raise KeyError('Optimizer type needs to be specified.')
    if not optimizer_kwargs['type'].lower() in optimizers_dict:
        raise ValueError('No valid optimizer specified.')
    optimizer = optimizers_dict[optimizer_kwargs.pop('type')]
    return optimizer(model_parameters, **optimizer_kwargs)


def get_scheduler_from_kwargs(optimizer: torch.optim.Optimizer,
                              **scheduler_kwargs,
                              ):
    """
    Builds and returns an scheduler for optimizer. The type of the
    scheduler is determined by kwarg type, the remaining kwargs are passed to
    the scheduler.

    Parameters
    ----------
    optimizer: torch.optim.optimizer.Optimizer
        optimizer for which the scheduler is used
    scheduler_kwargs:
        kwargs for scheduler; type needs to be one of [step, cosine,
        reduce_on_plateau], the remaining kwargs are used for
        specific scheduler kwargs, such as learning rate and momentum

    Returns
    -------
    scheduler
    """
    schedulers_dict = {
        'step': torch.optim.lr_scheduler.StepLR,
        'cosine': torch.optim.lr_scheduler.CosineAnnealingLR,
        'reduce_on_plateau': torch.optim.lr_scheduler.ReduceLROnPlateau,
    }
    if not 'type' in scheduler_kwargs:
        raise KeyError('Scheduler type needs to be specified.')
    if not scheduler_kwargs['type'].lower() in schedulers_dict:
        raise ValueError('No valid scheduler specified.')
    scheduler = schedulers_dict[scheduler_kwargs.pop('type')]
    return scheduler(optimizer, **scheduler_kwargs)


def perform_scheduler_step(scheduler,
                           loss=None,
                           ):
    """
    Wrapper for scheduler.step(). If scheduler is ReduceLROnPlateau,
    then scheduler.step(loss) is called, if not, scheduler.step().

    Parameters
    ----------

    scheduler:
        scheduler for learning rate
    loss:
        validation loss
    """
    if type(scheduler) == torch.optim.lr_scheduler.ReduceLROnPlateau:
        scheduler.step(loss)
    else:
        scheduler.step()