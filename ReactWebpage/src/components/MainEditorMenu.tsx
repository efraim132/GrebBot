import {Box, PageLayout} from "@primer/react";
import EditorHeader from "./EditorHeader.tsx";


function MainEditorMenu() {
    return (
        <Box style={{
            width: '100%',
            backgroundColor: 'white',
            borderRadius: 'var(--borderRadius-medium)',
            border: '1px solid var(--borderColor-muted)',
        }}> <PageLayout containerWidth="full">
            <PageLayout.Header>
                <EditorHeader/>
            </PageLayout.Header>
            <PageLayout.Pane resizable position="start" aria-label="Side pane">
                <Placeholder height={320} label="Pane"/>
            </PageLayout.Pane>
            <PageLayout.Content>
                <Placeholder height={640} label="Content"/>
            </PageLayout.Content>
            <PageLayout.Footer>
                <Placeholder height={64} label="Footer"/>
            </PageLayout.Footer>
        </PageLayout></Box>

    );
}

function Placeholder({height, children}: { height: number | string; children: React.ReactNode }) {
    return (
        <div
            style={{
                width: '100%',
                height,
                display: 'grid',
                placeItems: 'center',
                backgroundColor: 'var(--bgColor-inset)',
                borderRadius: 'var(--borderRadius-medium)',
                border: '1px solid var(--borderColor-muted)',
            }}
        >
            {children}
        </div>
    )
}

export default MainEditorMenu;