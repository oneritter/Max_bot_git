import { useEffect, useState } from 'react'
import { Table, Button, Space, Upload, Modal, Form, Input, Select, message, Popconfirm } from 'antd'
import { UploadOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload'
import api from '../api/client'

interface Doc {
  id: number
  title: string
  file_path: string
  file_type: string | null
  category_id: number | null
  sort_order: number
  is_active: boolean
}

interface Category {
  id: number
  name: string
  slug: string
  parent_id: number | null
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Doc[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [form] = Form.useForm()
  const [categoryFilter, setCategoryFilter] = useState<number | undefined>(undefined)

  const loadDocs = async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = {}
      if (categoryFilter !== undefined) params.category_id = categoryFilter
      const res = await api.get('/documents', { params })
      setDocs(res.data)
    } finally {
      setLoading(false)
    }
  }

  const loadCategories = async () => {
    const res = await api.get('/categories/flat')
    setCategories(res.data)
  }

  useEffect(() => {
    loadDocs()
    loadCategories()
  }, [categoryFilter])

  const handleUpload = async (values: { title: string; category_id?: number; sort_order?: number }) => {
    if (fileList.length === 0) {
      message.error('Выберите файл')
      return
    }
    const formData = new FormData()
    formData.append('title', values.title)
    if (values.category_id) formData.append('category_id', String(values.category_id))
    formData.append('sort_order', String(values.sort_order || 0))
    formData.append('file', fileList[0].originFileObj as Blob)

    try {
      await api.post('/documents', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      message.success('Документ загружен')
      setModalOpen(false)
      form.resetFields()
      setFileList([])
      loadDocs()
    } catch {
      message.error('Ошибка загрузки')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/documents/${id}`)
      message.success('Документ удалён')
      loadDocs()
    } catch {
      message.error('Ошибка удаления')
    }
  }

  const getCategoryName = (catId: number | null) => {
    if (!catId) return '—'
    const cat = categories.find((c) => c.id === catId)
    return cat ? cat.name : '—'
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: 'Название', dataIndex: 'title', key: 'title' },
    { title: 'Файл', dataIndex: 'file_path', key: 'file_path' },
    { title: 'Тип', dataIndex: 'file_type', key: 'file_type', width: 80 },
    {
      title: 'Раздел',
      dataIndex: 'category_id',
      key: 'category_id',
      render: (v: number | null) => getCategoryName(v),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: unknown, record: Doc) => (
        <Popconfirm title="Удалить документ?" onConfirm={() => handleDelete(record.id)}>
          <Button danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ]

  return (
    <>
      <h2>Документы</h2>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Фильтр по разделу"
          allowClear
          style={{ width: 250 }}
          value={categoryFilter}
          onChange={setCategoryFilter}
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Загрузить документ
        </Button>
      </Space>

      <Table columns={columns} dataSource={docs} rowKey="id" loading={loading} pagination={{ pageSize: 20 }} />

      <Modal
        title="Загрузка документа"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        okText="Загрузить"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" onFinish={handleUpload}>
          <Form.Item name="title" label="Название" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="category_id" label="Раздел">
            <Select
              allowClear
              placeholder="Выберите раздел"
              options={categories.map((c) => ({ value: c.id, label: c.name }))}
            />
          </Form.Item>
          <Form.Item name="sort_order" label="Порядок сортировки" initialValue={0}>
            <Input type="number" />
          </Form.Item>
          <Form.Item label="Файл" required>
            <Upload
              beforeUpload={() => false}
              fileList={fileList}
              onChange={({ fileList }) => setFileList(fileList)}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>Выбрать файл</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
