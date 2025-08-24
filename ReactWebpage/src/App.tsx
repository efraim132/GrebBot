import './App.css'
import {useState} from "react";
import WarningBanner from "./components/WarningBanner.tsx";
import MainEditorMenu from "./components/MainEditorMenu.tsx";

export default function App() {
    const [banner, setBanner] = useState(true)

    return (
        <>
            {banner && <WarningBanner toggleBannerFunction={()=> setBanner(!banner)} />}


            {!banner && <MainEditorMenu/>}

        </>
    )
}
