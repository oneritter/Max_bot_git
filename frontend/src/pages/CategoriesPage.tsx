import { useEffect, useState } from 'react'
import { Tree, Button, Modal, Form, Input, Select, Space, message, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { DataNode } from 'antd/es/tree'
import api from '../api/client'

interface CategoryNode {
  id: number
  name: string
  slug: string
  parent_id: number | null
  sort_order: number
  icon: string | null
  is_active: boolean
  children: CategoryNode[]
}

interface FlatCategory {
  id: number
  name: string
  slug: string
  parent_id: number | null
}

export default function CategoriesPage() {
  const [tree, setTree] = useState<CategoryNode[]>([])
  const [flatCategories, setFlatCategories] = useState<FlatCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form] = Form.useForm()

  const loadTree = async () => {
    setLoading(true)
    try {
      const [treeRes, flatRes] = await Promise.all([
        api.get('/categories'),
        api.get('/categories/flat'),
      ])
      setTree(treeRes.data)
      setFlatCategories(flatRes.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTree()
  }, [])

  const toTreeData = (nodes: CategoryNode[]): DataNode[] =>
    nodes.map((node) => ({
      key: node.id,
      title: (
        <Space>
          <span>{node.icon || ''} {node.name}</span>
          <span style={{ color: '#999', fontSize: 12 }}>({node.slug})</span>
          <Button size="small" icon={<EditOutlined />} onClick={(e) => { e.stopPropagation(); openEdit(node) }} />
          <Popconfirm title="Удалить раздел?" onConfirm={() => handleDelete(node.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} onClick={(e) => e.stopPropagation()} />
          </Popconfirm>
        </Space>
      ),
      children: node.children.length > 0 ? toTreeData(node.children) : undefined,
    }))

  const openCreate = () => {
    setEditingId(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (node: CategoryNode) => {
    setEditingId(node.id)
    form.setFieldsValue({
      name: node.name,
      slug: node.slug,
      parent_id: node.parent_id,
      sort_order: node.sort_order,
      icon: node.icon,
    })
    setModalOpen(true)
  }

  const handleSubmit = async (values: { name: string; slug: string; parent_id?: number; sort_order?: number; icon?: string }) => {
    try {
      if (editingId) {
        await api.patch(`/categories/${editingId}`, values)
        message.success('Раздел обновлён')
      } else {
        await api.post('/categories', values)
        message.success('Раздел создан')
      }
      setModalOpen(false)
      form.resetFields()
      loadTree()
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/categories/${id}`)
      message.success('Раздел удалён')
      loadTree()
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка удаления')
    }
  }

  return (
    <>
      <h2>Структура разделов</h2>
      <Button type="primary" icon={<PlusOutlined />} onClick={openCreate} style={{ marginBottom: 16 }}>
        Добавить раздел
      </Button>

      {loading ? (
        <p>Загрузка...</p>
      ) : tree.length === 0 ? (
        <p>Разделы не созданы. Нажмите "Добавить раздел".</p>
      ) : (
        <Tree treeData={toTreeData(tree)} defaultExpandAll showLine />
      )}

      <Modal
        title={editingId ? 'Редактировать раздел' : 'Создать раздел'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        okText={editingId ? 'Сохранить' : 'Создать'}
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="name" label="Название" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="slug" label="Slug (callback_data)" rules={[{ required: true }]}>
            <Input placeholder="например: pamyatki_oplata" />
          </Form.Item>
          <Form.Item name="parent_id" label="Родительский раздел">
            <Select
              allowClear
              placeholder="Корневой раздел"
              options={flatCategories.map((c) => ({ value: c.id, label: c.name }))}
            />
          </Form.Item>
          <Form.Item name="sort_order" label="Порядок сортировки" initialValue={0}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="icon" label="Иконка (эмодзи)">
            <Input placeholder="например: 📘" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
