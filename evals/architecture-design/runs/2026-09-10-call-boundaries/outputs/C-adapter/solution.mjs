const LIST_REASONS_SUCCESS_CODE = 200;

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function isPage(value) {
  return Number.isInteger(value) && value > 0;
}

function toReasonOption(row) {
  const option = {};
  if (!isRecord(row)) return option;
  if (typeof row.id === 'string') option.id = row.id;
  if (typeof row.name === 'string') option.label = row.name;
  return option;
}

/**
 * Read exactly the customer and page requested by the caller.
 * External dependency: deps.api.list({ customerId, page }).
 * Rejections and synchronous exceptions propagate to the existing request chain.
 */
export async function readReasons(input, deps) {
  if (
    !isRecord(input) ||
    typeof input.customerId !== 'string' ||
    input.customerId.trim().length === 0 ||
    !isPage(input.page)
  ) {
    return { kind: 'invalid-input' };
  }

  const response = await deps.api.list({
    customerId: input.customerId,
    page: input.page,
  });

  if (!isRecord(response) || response.code !== LIST_REASONS_SUCCESS_CODE) {
    return { kind: 'unconfirmed' };
  }

  const result = { kind: 'success' };
  if (Array.isArray(response.data)) {
    // Array.from also retains the position of a sparse entry as an empty view.
    result.options = Array.from(response.data, toReasonOption);
  }
  if (isPage(response.nextPage)) result.nextPage = response.nextPage;
  return result;
}
