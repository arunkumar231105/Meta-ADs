import { useState, useRef } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, Upload, Building2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { useCreateCompetitor } from '../../../hooks/queries/useCompetitors'
import Button from '../../../components/ui/Button'
import { cn } from '../../../lib/utils'

const schema = z.object({
  name:          z.string().min(1, 'Name is required'),
  domain:        z.string().min(1, 'Domain is required'),
  priority_tier: z.enum(['High', 'Medium', 'Low'], { message: 'Select a priority tier' }),
  niche:         z.string().min(1, 'Niche is required'),
  tags:          z.string().optional(),
})

function FieldError({ message }) {
  if (!message) return null
  return <p className="mt-1 text-xs text-danger-600">{message}</p>
}

function Label({ htmlFor, children, required }) {
  return (
    <label htmlFor={htmlFor} className="mb-1.5 block text-sm font-medium text-text-primary">
      {children}
      {required && <span className="ml-0.5 text-danger-500">*</span>}
    </label>
  )
}

const INPUT = cn(
  'h-9 w-full rounded-btn border border-border-default bg-white px-3',
  'text-sm text-text-primary placeholder:text-text-tertiary',
  'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
  'disabled:opacity-60'
)

export default function AddCompetitorModal({ open, onOpenChange }) {
  const [logoFile, setLogoFile]       = useState(null)
  const [logoPreview, setLogoPreview] = useState(null)
  const fileRef = useRef(null)

  const { mutate, isPending } = useCreateCompetitor({
    onSuccess: () => {
      toast.success('Competitor added successfully')
      onOpenChange(false)
    },
    onError: () => toast.error('Failed to add competitor'),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { priority_tier: 'Medium' },
  })

  const onSubmit = (data) => {
    const fd = new FormData()
    Object.entries(data).forEach(([k, v]) => { if (v) fd.append(k, v) })
    if (logoFile) fd.append('logo', logoFile)
    mutate(fd)
  }

  const handleClose = () => {
    onOpenChange(false)
    reset()
    setLogoFile(null)
    setLogoPreview(null)
  }

  const handleLogo = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLogoFile(file)
    const reader = new FileReader()
    reader.onload = (ev) => setLogoPreview(ev.target.result)
    reader.readAsDataURL(file)
  }

  return (
    <Dialog.Root open={open} onOpenChange={handleClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm data-[state=open]:animate-in data-[state=open]:fade-in-0" />
        <Dialog.Content
          className={cn(
            'fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2',
            'rounded-card border border-border-default bg-white shadow-xl',
            'data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95',
            'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
            'max-h-[90vh] overflow-y-auto'
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border-default px-6 py-4">
            <div>
              <Dialog.Title className="text-base font-semibold text-text-primary">
                Add Competitor
              </Dialog.Title>
              <Dialog.Description className="mt-0.5 text-xs text-text-secondary">
                Track a new competitor and their ad activity.
              </Dialog.Description>
            </div>
            <button
              onClick={handleClose}
              className="rounded-md p-1 text-text-tertiary hover:bg-gray-100 hover:text-text-primary focus-visible:outline-none"
            >
              <X size={18} />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 px-6 py-5">
            {/* Logo upload */}
            <div>
              <Label>Logo</Label>
              <div className="flex items-center gap-4">
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className={cn(
                    'flex h-16 w-16 flex-shrink-0 items-center justify-center',
                    'rounded-md border-2 border-dashed border-border-default bg-gray-50',
                    'hover:border-primary-400 hover:bg-primary-50 transition-colors overflow-hidden'
                  )}
                >
                  {logoPreview
                    ? <img src={logoPreview} alt="" className="h-full w-full object-cover" />
                    : <Building2 size={22} className="text-text-tertiary" />
                  }
                </button>
                <div>
                  <button
                    type="button"
                    onClick={() => fileRef.current?.click()}
                    className="flex items-center gap-1.5 text-sm font-medium text-primary-600 hover:underline"
                  >
                    <Upload size={13} /> Upload logo
                  </button>
                  <p className="mt-0.5 text-xs text-text-tertiary">PNG, JPG up to 2 MB</p>
                </div>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  onChange={handleLogo}
                  className="hidden"
                />
              </div>
            </div>

            {/* Name + Domain */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name" required>Name</Label>
                <input
                  id="name"
                  {...register('name')}
                  placeholder="e.g. BrandX"
                  className={cn(INPUT, errors.name && 'border-danger-400 focus:ring-danger-400')}
                />
                <FieldError message={errors.name?.message} />
              </div>
              <div>
                <Label htmlFor="domain" required>Domain</Label>
                <input
                  id="domain"
                  {...register('domain')}
                  placeholder="e.g. brandx.com"
                  className={cn(INPUT, errors.domain && 'border-danger-400 focus:ring-danger-400')}
                />
                <FieldError message={errors.domain?.message} />
              </div>
            </div>

            {/* Niche + Priority Tier */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="niche" required>Niche</Label>
                <input
                  id="niche"
                  {...register('niche')}
                  placeholder="e.g. Custom Printing"
                  className={cn(INPUT, errors.niche && 'border-danger-400 focus:ring-danger-400')}
                />
                <p className="mt-1 text-[10px] text-text-tertiary">Comma-separate multiple niches</p>
                <FieldError message={errors.niche?.message} />
              </div>
              <div>
                <Label htmlFor="priority_tier" required>Priority Tier</Label>
                <select
                  id="priority_tier"
                  {...register('priority_tier')}
                  className={cn(
                    INPUT,
                    'appearance-none cursor-pointer',
                    errors.priority_tier && 'border-danger-400 focus:ring-danger-400'
                  )}
                >
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
                <FieldError message={errors.priority_tier?.message} />
              </div>
            </div>

            {/* Tags */}
            <div>
              <Label htmlFor="tags">Tags</Label>
              <input
                id="tags"
                {...register('tags')}
                placeholder="e.g. direct competitor, holiday, Q2"
                className={INPUT}
              />
              <p className="mt-1 text-[10px] text-text-tertiary">Comma-separated tags for organisation</p>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 border-t border-border-default pt-4">
              <Button variant="outline" type="button" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" loading={isPending}>
                Add Competitor
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
