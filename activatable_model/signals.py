from django.dispatch import Signal


model_activations_changed = Signal(providing_args=['instances', 'is_active'])
