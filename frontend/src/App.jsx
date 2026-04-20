import {Routes, Route} from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Dashboard  from "./pages/Dashboard";
import Analysis  from "./pages/Analysis";
import Predict  from "./pages/Predict";

export default function App(){
    return(
        <Layout>
            <Routes>
                <Route path ="/" element = {<Home />}/>
                <Route path ="/dashboard" element = {<Dashboard  />}/>
                <Route path ="/analysis" element = {<Analysis  />}/>
                <Route path ="/predict" element = {<Predict  />}/>
            </Routes>
        </Layout>
    );
}