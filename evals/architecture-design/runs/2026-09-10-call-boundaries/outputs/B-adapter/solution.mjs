/**
 * Read the requested page through the supplied request boundary.
 * IDs are kept exactly as supplied; their domain-specific type is not
 * invented by this field adapter. Missing display fields remain absent.
 */
export async function readReasons(input, deps) {
  if (
    input == null ||
    typeof input !== 'object' ||
    input.customerId == null ||
    input.customerId === '' ||
    !Number.isInteger(input.page) ||
    input.page <= 0
  ) {
    return { kind: 'invalid-input' };
  }

  const response = await deps.api.list({
    customerId: input.customerId,
    page: input.page,
  });

  if (response?.code !== 200) {
    return { kind: 'unconfirmed' };
  }

  const result = { kind: 'success' };
  if (Array.isArray(response.data)) {
    result.options = Array.from(response.data, (row) => {
      const option = {};
      if (row !== null && typeof row === 'object') {
        if (row.id != null) option.id = row.id;
        if (row.name != null) option.label = row.name;
      }
      return option;
    });
  }
  if (response.nextPage != null) {
    result.nextPage = response.nextPage;
  }
  return result;
}
