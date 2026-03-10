import { useEffect, useState } from 'react'
import { Table, Tag, Button, Space, Input, Select, message, Popconfirm } from 'antd'
import { CheckOutlined, StopOutlined, SearchOutlined } from '@ant-design/icons'
import api from '../api/client'

interface User {
  id: number
  max_user_id: string
  username: string | null
  full_name: string | null
  phone: string | null
  status: string
  created_at: string | null
}

const statusColors: Record<string, string> = {
  pending: 'orange',
  approved: 'green',
  blocked: 'red',
}

const statusLabels: Record<string, string> = {
  pending: 'Ожидает',
  approved: 'Одобрен',
  blocked: 'Заблокирован',
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)

  const loadUsers = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const res = await api.get('/users', { params })
      setUsers(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [statusFilter])

  const changeStatus = async (userId: number, newStatus: string) => {
    try {
      await api.patch(`/users/${userId}`, { status: newStatus })
      message.success('Статус обновлён')
      loadUsers()
    } catch {
      message.error('Ошибка обновления')
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: 'ФИО',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (v: string | null) => v || '—',
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
      render: (v: string | null) => v || '—',
    },
    {
      title: 'Телефон',
      dataIndex: 'phone',
      key: 'phone',
      render: (v: string | null) => v || '—',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={statusColors[status]}>{statusLabels[status] || status}</Tag>
      ),
    },
    {
      title: 'Дата',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (v: string | null) => v ? new Date(v).toLocaleDateString('ru-RU') : '—',
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: unknown, record: User) => (
        <Space>
          {record.status !== 'approved' && (
            <Popconfirm title="Одобрить пользователя?" onConfirm={() => changeStatus(record.id, 'approved')}>
              <Button type="primary" size="small" icon={<CheckOutlined />}>Одобрить</Button>
            </Popconfirm>
          )}
          {record.status !== 'blocked' && (
            <Popconfirm title="Заблокировать пользователя?" onConfirm={() => changeStatus(record.id, 'blocked')}>
              <Button danger size="small" icon={<StopOutlined />}>Блок</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <>
      <h2>Пользователи</h2>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="Поиск по ФИО, телефону"
          prefix={<SearchOutlined />}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onPressEnter={loadUsers}
          style={{ width: 250 }}
        />
        <Select
          placeholder="Статус"
          allowClear
          style={{ width: 150 }}
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { value: 'pending', label: 'Ожидает' },
            { value: 'approved', label: 'Одобрен' },
            { value: 'blocked', label: 'Заблокирован' },
          ]}
        />
        <Button onClick={loadUsers}>Обновить</Button>
      </Space>
      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
      />
    </>
  )
}
