export async function ensureDraft({ customerId }, deps) {
  const draft = await deps.api.find({ customerId });
  if (draft !== null) {
    return draft;
  }
  return deps.api.create({ customerId });
}

export async function capturePhoto(input, deps) {
  const session = await deps.device.open(input);
  try {
    const result = await session.capture();
    if (result.kind === 'cancelled') {
      return { kind: 'cancelled' };
    }

    const { temporaryPath } = result;
    try {
      const { uri } = await deps.files.adopt(temporaryPath);
      return { kind: 'success', uri };
    } finally {
      await deps.files.remove(temporaryPath);
    }
  } finally {
    await session.close();
  }
}
