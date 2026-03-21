import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { TopPage } from './pages/TopPage'
import { CreateRoomPage } from './pages/CreateRoomPage'
import { JoinPage } from './pages/JoinPage'
import { RoomJoinPage } from './pages/RoomJoinPage'
import { EvaluatePage } from './pages/EvaluatePage'
import { ResultPage } from './pages/ResultPage'
import { ReportPreviewPage } from './pages/ReportPreviewPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TopPage />} />
        <Route path="/create" element={<CreateRoomPage />} />
        <Route path="/join" element={<JoinPage />} />
        <Route path="/room/:roomId/join" element={<RoomJoinPage />} />
        <Route path="/room/:roomId/evaluate" element={<EvaluatePage />} />
        <Route path="/room/:roomId/result" element={<ResultPage />} />
        <Route path="/report-preview" element={<ReportPreviewPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
