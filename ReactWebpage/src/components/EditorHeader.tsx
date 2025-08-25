import {Button, ButtonGroup, Link, PageHeader} from "@primer/react";
import {BroadcastIcon, KeyIcon, RocketIcon} from "@primer/octicons-react";

import "./EditorHeader.css"
import DiscordIcon from "./DiscordIcon.tsx";

function EditorHeader() {
    return (
        <>
            <PageHeader role="banner" aria-label="Title">
                <PageHeader.TitleArea>

                    <DiscordIcon size={"large"} /><PageHeader.Title>GrebBot Editor</PageHeader.Title>

                </PageHeader.TitleArea>
                <PageHeader.Actions>
                    <ButtonGroup>
                        <Button leadingVisual={RocketIcon}>Start Features</Button>
                        <Button leadingVisual={BroadcastIcon  }>Connectivity</Button>
                        <Button trailingVisual={KeyIcon} variant={"primary"}>Sign In</Button>
                    </ButtonGroup>
                </PageHeader.Actions>
                <PageHeader.Description>
    <span style={{fontSize: 'var(--text-body-size-medium)', color: 'var(--fgColor-muted)'}}>
      <Link href="https://github.com/efraim132/GrebBot" style={{fontWeight: 'var(--base-text-weight-semibold)'}}>
        Repository
      </Link>
    </span> {'– A web-based editor for configuring the GrebBot Discord bot with ease.'}
                </PageHeader.Description>
            </PageHeader>
        </>
    );
}

export default EditorHeader;