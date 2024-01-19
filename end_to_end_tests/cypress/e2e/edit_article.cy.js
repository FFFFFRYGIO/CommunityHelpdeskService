describe('template spec', () => {

    beforeEach(() => {
        cy.register_user('testuser', 'ph1shstix!');
        cy.login_user('testuser', 'ph1shstix!');
    });

    it('Edit Article Test', () => {
        cy.visit('http://127.0.0.1:8000/user_app/create_article/');

        cy.get('#id_title').type('Test Article Title');
        cy.get('#id_tags').type('tag1, tag2, tagtest');

        cy.get('#id_form-0-title').type('Test Step 1 title');
        cy.get('#id_form-0-description1').type('Test Step 1 description1');
        cy.get('#id_form-0-description2').type('Test Step 1 description2');

        cy.get('#add-step-button').click();

        cy.get('#id_form-1-title').type('Test Step 2 title');
        cy.get('#id_form-1-description1').type('Test Step 2 description1');
        cy.get('#id_form-1-description2').type('Test Step 2 description2');

        cy.get('button[type="submit"]').click();

        cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

        cy.get('.card-body').should('contain', 'Test Article Title');
        cy.get('.card-body').should('contain', 'testuser');
        cy.get('.card-body').should('contain', 'Steps: 2');
        cy.get('.card-body').should('contain', '\n' +
            '                    Tags: \n' +
            '                    #tag1 \n' +
            '                \n' +
            '                    #tagtest \n' +
            '                \n' +
            '                    #tag2\n' +
            '                \n' +
            '                ');

        cy.get('button[name="view_article"]').click();

        cy.get('button[name="edit_article"]').click();

        cy.get('#id_title').type('Test Article Title');
        cy.get('#id_tags').type('tagedit');

        cy.get('#id_form-0-title').clear().type('Test Step 1 title edited');
        cy.get('#id_form-0-description1').clear().type('Test Step 1 description1 edited');
        cy.get('#id_form-0-description2').clear().type('Test Step 1 description2 edited');

        // cy.get('#remove-step-button').click();
        // cy.get('#add-step-button').click();
        //
        // cy.get('#id_form-1-title').clear().type('Test New Step 2 title');
        // cy.get('#id_form-1-description1').clear().type('New Test Step 2 description1');
        // cy.get('#id_form-1-description2').clear().type('New Test Step 2 description2');

        cy.get('#id_form-1-title').clear().type('Test Step 2 title edited');
        cy.get('#id_form-1-description1').clear().type('New Step 2 description1 edited');
        cy.get('#id_form-1-description2').clear().type('New Step 2 description2 edited');

        cy.get('#add-step-button').click();

        cy.get('#id_form-2-title').clear().type('Test New Step 3 title');
        cy.get('#id_form-2-description1').clear().type('New Test Step 3 description1');
        cy.get('#id_form-2-description2').clear().type('New Test Step 3 description2');

        cy.get('button[type="submit"]').click();

        cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

        cy.get('.card-body').should('contain', 'Test Article Title');
        cy.get('.card-body').should('contain', 'testuser');
        cy.get('.card-body').should('contain', 'Steps: 3');
        cy.get('.card-body').should('contain', '\n' +
            '                    Tags: \n' +
            '                    #tagedit \n' +
            '                \n' +
            '                ');

    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.cleanup_user('testuser');
    });

});
