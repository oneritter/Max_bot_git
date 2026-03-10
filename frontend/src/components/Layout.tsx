import { Layout as AntLayout, Menu } from 'antd'
import {
  DashboardOutlined,
  UserOutlined,
  FileOutlined,
  AppstoreOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Sider, Content, Header } = AntLayout

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Статистика' },
    { key: '/users', icon: <UserOutlined />, label: 'Пользователи' },
    { key: '/documents', icon: <FileOutlined />, label: 'Документы' },
    { key: '/categories', icon: <AppstoreOutlined />, label: 'Разделы' },
  ]

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div style={{ color: '#fff', textAlign: 'center', padding: '16px', fontSize: '18px', fontWeight: 'bold' }}>
          Finbox Admin
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
        <Menu
          theme="dark"
          mode="inline"
          selectable={false}
          style={{ position: 'absolute', bottom: 0, width: '100%' }}
          items={[{ key: 'logout', icon: <LogoutOutlined />, label: 'Выход' }]}
          onClick={handleLogout}
        />
      </Sider>
      <AntLayout>
        <Header style={{ background: '#fff', padding: '0 24px', fontSize: '16px' }}>
          Панель администрирования
        </Header>
        <Content style={{ margin: '24px', padding: '24px', background: '#fff', borderRadius: '8px' }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  )
}
