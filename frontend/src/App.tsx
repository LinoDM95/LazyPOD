import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { api } from './api/client';
import { usePollingDraft } from './hooks/usePollingDraft';

const draftSchema = z.object({
  template_id: z.coerce.number().min(1),
  title: z.string().min(3),
  price: z.string().min(1),
  tags: z.string().optional(),
});

type DraftForm = z.infer<typeof draftSchema>;

function App() {
  const queryClient = useQueryClient();
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: api.health });
  const { data: templates = [] } = useQuery({ queryKey: ['templates'], queryFn: api.templates });
  const { data: drafts = [] } = useQuery({ queryKey: ['drafts'], queryFn: api.drafts });
  const [selectedDraft] = drafts;
  const draftDetail = usePollingDraft(selectedDraft?.id ?? null);

  const uploadMutation = useMutation({ mutationFn: api.uploadAssets });
  const createMutation = useMutation({
    mutationFn: api.createDrafts,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['drafts'] }),
  });
  const pushMutation = useMutation({
    mutationFn: api.pushDraft,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drafts'] });
      if (selectedDraft) {
        queryClient.invalidateQueries({ queryKey: ['draft', selectedDraft.id] });
      }
    },
  });

  const { register, handleSubmit } = useForm<DraftForm>({
    resolver: zodResolver(draftSchema),
    defaultValues: { title: 'MVP Draft', price: '19.99' },
  });

  const onSubmit = async (values: DraftForm) => {
    if (!uploadMutation.data?.length) return;
    await createMutation.mutateAsync({
      drafts: [
        {
          ...values,
          tags: values.tags?.split(',').map((item) => item.trim()).filter(Boolean) ?? [],
          asset_ids: uploadMutation.data.map((item) => item.id),
        },
      ],
    });
  };

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <h1 className="mb-2 text-3xl font-bold">LazyPOD MVP running</h1>
      <p className="mb-6">Backend health: {health?.status ?? 'loading...'}</p>

      <section className="mb-6 rounded border border-slate-700 p-4">
        <h2 className="mb-2 font-semibold">Templates</h2>
        <ul className="space-y-1 text-sm">
          {templates.map((template) => (
            <li key={template.id}>{template.name} ({template.gelato_template_id})</li>
          ))}
        </ul>
      </section>

      <section className="mb-6 rounded border border-slate-700 p-4">
        <h2 className="mb-2 font-semibold">Upload + Draft Create</h2>
        <input
          type="file"
          multiple
          className="mb-3 block"
          onChange={(event) => {
            const files = Array.from(event.target.files ?? []);
            if (files.length) uploadMutation.mutate(files);
          }}
        />
        <form onSubmit={handleSubmit(onSubmit)} className="grid gap-2 md:max-w-md">
          <select {...register('template_id')} className="rounded bg-slate-800 p-2">
            <option value="">Template wählen</option>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>{template.name}</option>
            ))}
          </select>
          <input {...register('title')} placeholder="Title" className="rounded bg-slate-800 p-2" />
          <input {...register('price')} placeholder="Price" className="rounded bg-slate-800 p-2" />
          <input {...register('tags')} placeholder="tags comma separated" className="rounded bg-slate-800 p-2" />
          <button type="submit" className="rounded bg-indigo-500 p-2">Create draft</button>
        </form>
      </section>

      <section className="rounded border border-slate-700 p-4">
        <h2 className="mb-2 font-semibold">Draft detail + push</h2>
        {draftDetail.data ? (
          <div className="space-y-2 text-sm">
            <div>{draftDetail.data.title} - status: {draftDetail.data.status}</div>
            <button
              type="button"
              className="rounded bg-emerald-500 p-2"
              onClick={() => pushMutation.mutate(draftDetail.data!.id)}
            >
              Push draft
            </button>
          </div>
        ) : <div>No draft yet.</div>}
      </section>
    </main>
  );
}

export default App;
