/** Query the customer's draft; create only when the API explicitly returns null. */
export async function ensureDraft({ customerId }, deps) {
  const draft = await deps.api.find({ customerId });
  if (draft !== null) return draft;
  return await deps.api.create({ customerId });
}

/** Own one capture session and release its temporary file before returning. */
export async function capturePhoto(input, deps) {
  const session = await deps.device.open(input);
  try {
    const result = await session.capture();
    if (result.kind === 'cancelled') return { kind: 'cancelled' };

    const { temporaryPath } = result;
    try {
      const photo = await deps.files.adopt(temporaryPath);
      return { kind: 'success', uri: photo.uri };
    } finally {
      await deps.files.remove(temporaryPath);
    }
  } finally {
    await session.close();
  }
}
