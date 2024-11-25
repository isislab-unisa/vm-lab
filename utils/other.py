from typing import List


def count_non_none_variables(variables: List) -> int:
	"""Counts the number of variables that are not `None` in a list."""
	non_none_count = 0
	for variable in variables:
		if variable is not None:
			non_none_count += 1

	return non_none_count