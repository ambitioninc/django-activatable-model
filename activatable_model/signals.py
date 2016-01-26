from django.dispatch import Signal


model_activations_changed = Signal(providing_args=['instance_ids', 'is_active'])

model_activations_updated = Signal(providing_args=['instance_ids', 'is_active'])
