export async function ensureDraft({ customerId }, deps) {
  const draft = await deps.api.find({ customerId });
  if (draft === null) {
    return await deps.api.create({ customerId });
  }
  return draft;
}

export async function capturePhoto(input, deps) {
  const session = await deps.device.open(input);
  try {
    const capture = await session.capture();
    if (capture.kind === 'cancelled') {
      return { kind: 'cancelled' };
    }
    try {
      const photo = await deps.files.adopt(capture.temporaryPath);
      return { kind: 'success', uri: photo.uri };
    } finally {
      await deps.files.remove(capture.temporaryPath);
    }
  } finally {
    await session.close();
  }
}
