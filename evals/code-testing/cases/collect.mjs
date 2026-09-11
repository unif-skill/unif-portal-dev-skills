export async function collect(input, deps) {
  const photo = await deps.capture({ ownerId: input.ownerId });
  if (photo.kind === 'cancelled') return null;
  return deps.save({ ownerId: input.ownerId, uri: photo.uri });
}
