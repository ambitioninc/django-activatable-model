from django.dispatch import Signal


model_activations_changed = Signal(providing_args=['instance_ids', 'is_active'])
