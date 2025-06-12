from typing import Optional

from . import levels
from .exceptions import ValidationError


class HtmlTagAttribute:
    DEFAULT_ERROR_LEVEL = levels.ERROR

    def __init__(  # noqa: PLR0913
        self,
        name: str | None = None,
        root: Optional["TagChecker"] = None,  # noqa: F821
        value: str | None = None,
        required: bool = True,
        ignore_case: bool = False,
        expected: str | None = None,
        choices: list[str] | None = None,
    ):
        self.name = name
        self.root = root
        self.required = required
        self.value = value
        self.expected = expected
        self.choices = choices
        self.ignore_case = ignore_case
        self.errors = []

        if all([self.expected, self.choices]):
            raise AttributeError("You cant set both of parameters: expected and choices")
        if any([self.expected, self.choices]):
            self.required = True

    def __repr__(self):
        return f'<Attr:{self.name}="{self.value}">'

    @property
    def error_level(self) -> levels.ErrorLevel:
        if self.errors:
            max_level_error = max(self.errors, key=lambda validation_error: validation_error.level)
            return max_level_error.level
        return levels.SUCCESS

    def bind(self, root: "TagChecker", field_name: str) -> None:  # noqa: F821
        self.root = root
        if self.name is None:
            self.name = field_name

    def _normalize(self, value: str | None) -> str | None:
        if value is None:
            return None
        return value.lower() if self.ignore_case else value

    def run_validators(self) -> None:
        if self.required:
            try:
                self.required_validation()
            except ValidationError as error:
                self.errors.append(error)

        if self.value is not None:
            try:
                self.expected_validation()
                self.choices_validation()
            except ValidationError as error:
                self.errors.append(error)
        try:
            self.validate()
        except ValidationError as error:
            self.errors.append(error)

    def required_validation(self) -> None:
        if self.value is None:
            raise ValidationError(
                message=f'Attr "{self.name}" is required',
                level=self.DEFAULT_ERROR_LEVEL,
            )

    def expected_validation(self) -> None:
        if self.expected is None:
            return
        if self._normalize(value=self.value) != self._normalize(value=self.expected):
            raise ValidationError(
                message=f'Attr value must be "{self.expected}", actual "{self.value}"',
                level=self.DEFAULT_ERROR_LEVEL,
            )

    def choices_validation(self) -> None:
        if self.choices is None:
            return
        if self._normalize(value=self.value) not in [self._normalize(value=choice) for choice in self.choices]:
            raise ValidationError(
                message=f'Attr value must be on of {self.choices}, actual "{self.value}"',
                level=self.DEFAULT_ERROR_LEVEL,
            )

    def validate(self) -> None:
        """Hook"""



HTTP_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
    "TRACE",
    "CONNECT",
]


class FormMethod(HtmlTagAttribute):
    def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
        super().__init__(*args, choices=HTTP_METHODS, ignore_case=True, **kwargs)


HTML_INPUT_TYPES_ATTRS = [
    "button",
    "checkbox",
    "color",
    "date",
    "datetime-local",
    "email",
    "file",
    "hidden",
    "image",
    "month",
    "number",
    "password",
    "radio",
    "range",
    "reset",
    "search",
    "submit",
    "tel",
    "text",
    "time",
    "url",
    "week",
]


class InputType(HtmlTagAttribute):
    def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
        super().__init__(
            *args,
            choices=HTML_INPUT_TYPES_ATTRS,
            ignore_case=True,
            **kwargs,
        )


class ClassAttr(HtmlTagAttribute):
    def __init__(
        self,
        *args,  # noqa: ANN002
        contains: set[str] | None = None,
        **kwargs,  # noqa: ANN003
    ):
        super().__init__(*args, ignore_case=False, name="class", choices=None, **kwargs)
        self.contains = contains
