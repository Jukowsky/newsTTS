import { Routes, Route } from "react-router-dom";
import PortalSelect from "./pages/PortalSelect";
import ArticleList from "./pages/ArticleList";
import Admin from "./pages/Admin";

export default function App() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <Routes>
        <Route path="/" element={<PortalSelect />} />
        <Route path="/portal/:portalId" element={<ArticleList />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </div>
  );
}
