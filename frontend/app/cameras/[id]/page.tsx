export default async function CameraDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div>
      <h2 className="text-2xl font-semibold">카메라 상세</h2>
      <p className="mt-2 text-muted-foreground">카메라 ID: {id}</p>
    </div>
  );
}
