const REASONS_SUCCESS_CODE = 200;

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function toOption(row) {
  const option = {};
  if (!isRecord(row)) return option;
  if (typeof row.id === 'string') option.id = row.id;
  if (typeof row.name === 'string') option.label = row.name;
  return option;
}

/** Read exactly one requested page; request errors propagate to the caller. */
export async function readReasons(input, deps) {
  if (
    !isRecord(input) ||
    typeof input.customerId !== 'string' ||
    input.customerId.trim().length === 0 ||
    !Number.isInteger(input.page) ||
    input.page < 1
  ) {
    return { kind: 'invalid-input' };
  }

  const response = await deps.api.list({
    customerId: input.customerId,
    page: input.page,
  });
  if (!isRecord(response) || response.code !== REASONS_SUCCESS_CODE) {
    return { kind: 'unconfirmed' };
  }

  const result = { kind: 'success' };
  if (Array.isArray(response.data)) {
    result.options = Array.from(response.data, toOption);
  }
  if (Number.isInteger(response.nextPage) && response.nextPage > 0) {
    result.nextPage = response.nextPage;
  }
  return result;
}
