from .models import Tag


def sections_processor(request):
	tags = Tag.objects.all()
	return {'tags': tags}