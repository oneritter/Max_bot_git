import { useEffect, useState } from 'react'
import { Card, Col, Row, Statistic, Spin } from 'antd'
import {
  UserOutlined,
  FileOutlined,
  QuestionCircleOutlined,
  BookOutlined,
} from '@ant-design/icons'
import api from '../api/client'

interface Stats {
  users: { total: number; pending: number; approved: number; blocked: number }
  documents: number
  categories: number
  training_requests: number
  feedback: { total: number; unresolved: number }
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/stats').then((res) => {
      setStats(res.data)
      setLoading(false)
    })
  }, [])

  if (loading || !stats) return <Spin size="large" />

  return (
    <>
      <h2>Статистика</h2>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Всего пользователей" value={stats.users.total} prefix={<UserOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Ожидают одобрения" value={stats.users.pending} valueStyle={{ color: '#faad14' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Одобрены" value={stats.users.approved} valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Заблокированы" value={stats.users.blocked} valueStyle={{ color: '#f5222d' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Документов" value={stats.documents} prefix={<FileOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Заявок на обучение" value={stats.training_requests} prefix={<BookOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Вопросов" value={stats.feedback.total} prefix={<QuestionCircleOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Нерешённых вопросов" value={stats.feedback.unresolved} valueStyle={{ color: '#faad14' }} />
          </Card>
        </Col>
      </Row>
    </>
  )
}
