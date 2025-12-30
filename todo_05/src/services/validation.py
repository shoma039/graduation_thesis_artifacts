from ..lib.errors import ValidationError


def require_title(title: str):
    if not title or not title.strip():
        raise ValidationError('タイトルは必須です', field='title')
    if len(title) > 200:
        raise ValidationError('タイトルが長すぎます（200文字以内）', field='title')
