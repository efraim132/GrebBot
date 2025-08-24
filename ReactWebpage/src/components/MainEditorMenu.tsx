import {Box, Button, Heading, Stack} from "@primer/react";
import {MarkGithubIcon} from "@primer/octicons-react";
import DiscordIcon from "./DiscordIcon.tsx";
import MyActionMenu from "../myActionMenu.tsx";


function MainEditorMenu() {
    return (
        <Box
            sx={{
                backgroundColor: 'white',
                borderRadius: 'var(--borderRadius-medium)',
                border: 'var(--borderWidth-thin) solid var(--borderColor-muted)',
                padding: 'var(--stack-padding-spacious)',
            }}
        >
            <Heading className="mb-2" as="h2">
                <MarkGithubIcon size={64}/> GrebBot Controls
            </Heading>
            <Stack direction="vertical">
                <Button onClick={() => alert('Hello, Primer!')}>Click me</Button>
                <MyActionMenu/>
            </Stack>
            <DiscordIcon/>
        </Box>
    );
}
export default MainEditorMenu;